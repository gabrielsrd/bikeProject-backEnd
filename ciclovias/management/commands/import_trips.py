from django.core.management.base import BaseCommand
import pandas as pd
from ciclovias.models import Station, Trip
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import re
from tqdm import tqdm
from django.db import transaction
import time
import os
from zoneinfo import ZoneInfo

class Command(BaseCommand):
    help = 'Import trips from consolidated CSV file to database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to consolidated CSV file')
        parser.add_argument('--batch-size', type=int, default=5000,
                            help='Batch size for bulk operations')
        parser.add_argument('--test-run', action='store_true',
                            help='Import only first 1000 rows for testing')
        parser.add_argument('--limit', type=int, default=None,
                            help='Import only first N rows (alternative to --test-run)')
        parser.add_argument('--chunk-rows', type=int, default=100000,
                            help='Number of CSV rows to read per chunk (streaming)')
        parser.add_argument('--precount', action='store_true',
                            help='Pre-count total rows for accurate progress (slight upfront cost)')
        parser.add_argument('--total-rows', type=int, default=None,
                            help='Provide known total rows to enable accurate progress')
        parser.add_argument('--estimate-sample', type=int, default=20000,
                            help='Number of lines to sample for row count estimation when not pre-counting')
        parser.add_argument('--assume-tz', type=str, default=None,
                            help='Timezone name to assume for naive timestamps (e.g., UTC or America/Sao_Paulo). Defaults to Django TIME_ZONE.')
        parser.add_argument('--station-id-min', type=int, default=None,
                            help='Import only stations/trips with station_id >= this value')
        parser.add_argument('--station-id-max', type=int, default=None,
                            help='Import only stations/trips with station_id <= this value')
        parser.add_argument('--max-trips', type=int, default=None,
                            help='Maximum number of trips to import after filtering')

    def extract_station_id(self, name):
        """Extract station ID from station name (same logic as views.py)"""
        if not isinstance(name, str):
            return None
        match = re.search(r'(\d+)', name)
        return int(match.group(1)) if match else None

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        test_run = options['test_run']
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS("Starting CSV import..."))
        
        try:
            # Stream CSV in chunks to avoid loading entire file into memory
            chunk_rows = options.get('chunk_rows') or 100000
            self.stdout.write(f"Reading CSV file in chunks of {chunk_rows} rows: {csv_file}")

            # Build read_csv kwargs for streaming
            read_kwargs = {
                'chunksize': chunk_rows,
                # Avoid dtype warnings and speed up parsing
                'dtype': {
                    'trip_id': 'string',
                    'duration_seconds': 'float64',
                    'initial_station_name': 'string',
                    'final_station_name': 'string',
                    'start_time': 'string',
                    'end_time': 'string',
                    'birth_year': 'string',
                },
                'usecols': [
                    'trip_id', 'duration_seconds',
                    'initial_station_name', 'start_time',
                    'final_station_name', 'end_time',
                    'birth_year',
                    'initial_station_latitude', 'initial_station_longitude',
                    'final_station_latitude', 'final_station_longitude'
                ],
            }

            # Apply limits for test runs
            rows_to_read = None
            if test_run:
                rows_to_read = 1000
                self.stdout.write(self.style.WARNING("TEST RUN: Importing only first 1000 rows"))
            elif limit:
                rows_to_read = limit
                self.stdout.write(self.style.WARNING(f"LIMITED IMPORT: Importing only first {limit} rows"))

            # Determine expected total rows for progress (Phase 1)
            expected_total_rows = options.get('total_rows')
            if expected_total_rows is None:
                if options.get('precount'):
                    expected_total_rows = self.count_csv_rows(csv_file)
                    style_fn = getattr(self.style, 'NOTICE', self.style.WARNING)
                    self.stdout.write(style_fn(f"Pre-counted total rows: {expected_total_rows}"))
                else:
                    expected_total_rows = self.estimate_total_rows(csv_file, options.get('estimate_sample') or 20000)
                    if expected_total_rows:
                        self.stdout.write(self.style.WARNING(
                            f"Estimated total rows: ~{expected_total_rows} (use --precount for exact)"
                        ))
            # Respect explicit limits
            if rows_to_read is not None and expected_total_rows is not None:
                expected_total_rows = min(expected_total_rows, rows_to_read)

            # Phase 1: Import stations by scanning chunks
            self.stdout.write("Phase 1: Importing stations...")
            total_rows_seen = 0
            phase1_start_time = time.time()
            for chunk in pd.read_csv(csv_file, **read_kwargs):
                # Respect rows_to_read limit
                if rows_to_read is not None and total_rows_seen >= rows_to_read:
                    break
                if rows_to_read is not None and total_rows_seen + len(chunk) > rows_to_read:
                    chunk = chunk.iloc[: max(0, rows_to_read - total_rows_seen)]

                total_rows_seen += len(chunk)
                self.import_stations(chunk)
                # Progress during Phase 1
                if expected_total_rows:
                    elapsed = max(0.001, time.time() - phase1_start_time)
                    pct = (total_rows_seen / expected_total_rows)
                    pct_display = min(100.0, pct * 100.0)
                    rate = total_rows_seen / elapsed
                    remaining = max(0, expected_total_rows - total_rows_seen)
                    eta_sec = int(remaining / rate) if rate > 0 else 0
                    self.stdout.write(
                        f"  Stations pass progress: {total_rows_seen}/{expected_total_rows} "
                        f"({pct_display:.1f}%), ~{eta_sec}s remaining at {rate:.0f} rows/s"
                    )
                else:
                    self.stdout.write(f"  Stations pass progress: scanned {total_rows_seen} rows...")

            self.stdout.write(self.style.SUCCESS(f"  ✓ Stations pass complete (scanned {total_rows_seen} rows)"))

            # Phase 2: Import trips by scanning chunks
            self.stdout.write("Phase 2: Importing trips...")
            # Use the number discovered in Phase 1 for precise progress in Phase 2
            total_rows_phase2 = rows_to_read if rows_to_read is not None else total_rows_seen
            phase2_processed = 0
            phase2_start_time = time.time()

            # Build station map once for the entire Phase 2
            sid_min = options.get('station_id_min')
            sid_max = options.get('station_id_max')
            max_trips = options.get('max_trips')
            station_map = {s.station_id: s for s in Station.objects.all() if s.station_id is not None}

            # Determine timezone to assume for naive timestamps
            assume_tz_name = options.get('assume_tz')
            if assume_tz_name:
                try:
                    assume_tz = ZoneInfo(assume_tz_name)
                except Exception:
                    self.stdout.write(self.style.WARNING(f"Invalid --assume-tz '{assume_tz_name}', defaulting to Django TIME_ZONE"))
                    assume_tz = timezone.get_default_timezone()
            else:
                assume_tz = timezone.get_default_timezone()

            total_rows_seen_trips = 0
            imported_total_trips = 0
            for chunk in pd.read_csv(csv_file, **read_kwargs):
                if rows_to_read is not None and total_rows_seen_trips >= rows_to_read:
                    break
                if rows_to_read is not None and total_rows_seen_trips + len(chunk) > rows_to_read:
                    chunk = chunk.iloc[: max(0, rows_to_read - total_rows_seen_trips)]

                total_rows_seen_trips += len(chunk)
                imported_in_chunk = self.import_trips(
                    chunk,
                    batch_size,
                    station_map,
                    assume_tz,
                    station_id_min=sid_min,
                    station_id_max=sid_max,
                    max_to_import=(max_trips - imported_total_trips) if max_trips is not None else None,
                )
                imported_total_trips += imported_in_chunk

                # Progress output with ETA
                phase2_processed += len(chunk)
                elapsed = max(0.001, time.time() - phase2_start_time)
                rate = phase2_processed / elapsed  # rows/sec
                remaining = max(0, total_rows_phase2 - phase2_processed)
                eta_sec = remaining / rate if rate > 0 else 0
                self.stdout.write(
                    f"  Trips progress: {phase2_processed}/{total_rows_phase2} "
                    f"({(phase2_processed/total_rows_phase2*100.0):.1f}%), "
                    f"~{int(eta_sec)}s remaining at {rate:.0f} rows/s; "
                    f"imported {imported_total_trips}{f'/{max_trips}' if max_trips else ''} trips"
                )

                if max_trips is not None and imported_total_trips >= max_trips:
                    self.stdout.write(self.style.SUCCESS(
                        f"Reached --max-trips cap ({max_trips}). Stopping early."
                    ))
                    break

            self.stdout.write(self.style.SUCCESS("Import completed successfully!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            raise

    def import_stations(self, df):
        """Import unique stations from the CSV data (no filtering)"""
        stations_data = set()
        
        # Extract unique stations from both initial and final station columns
        for _, row in df.iterrows():
            for station_type in ['initial', 'final']:
                name = row[f'{station_type}_station_name']
                lat = row[f'{station_type}_station_latitude']
                lon = row[f'{station_type}_station_longitude']
                
                if pd.notna(name) and str(name).strip():
                    station_id = self.extract_station_id(name)
                    lat_val = float(lat) if pd.notna(lat) else None
                    lon_val = float(lon) if pd.notna(lon) else None
                    
                    stations_data.add((
                        station_id, 
                        str(name).strip(), 
                        lat_val,
                        lon_val
                    ))
        
        # Create station objects
        station_objects = []
        for station_id, name, lat, lon in stations_data:
            station_objects.append(Station(
                station_id=station_id,
                name=name,
                latitude=lat,
                longitude=lon
            ))
        
        # Bulk create stations (ignore conflicts for existing stations)
        if station_objects:
            with transaction.atomic():
                Station.objects.bulk_create(station_objects, ignore_conflicts=True)
        
        self.stdout.write(f"  ✓ Processed {len(station_objects)} unique stations")

    def import_trips(self, df, batch_size, station_map=None, assume_tz=None,
                     station_id_min=None, station_id_max=None, max_to_import=None):
        """Import trips from a dataframe chunk in batches with optional station_id range filtering and a cap on total imported."""
        total_rows = len(df)
        imported_count = 0
        error_count = 0

        # Build station map if not provided (fallback)
        if station_map is None:
            station_map = {}
            for station in Station.objects.all():
                if station.station_id is not None:
                    station_map[station.station_id] = station

        # Fallback timezone
        if assume_tz is None:
            assume_tz = timezone.get_default_timezone()

        reached_cap = False
        for start_idx in range(0, total_rows, batch_size):
            if reached_cap:
                break
            end_idx = min(start_idx + batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]

            self.stdout.write(f"  Processing batch {start_idx + 1}-{end_idx} of {total_rows}")

            trip_objects = []
            for _, row in batch.iterrows():
                try:
                    # Parse timestamps
                    start_time = parse_datetime(str(row['start_time'])) if pd.notna(row['start_time']) else None
                    end_time = parse_datetime(str(row['end_time'])) if pd.notna(row['end_time']) else None

                    # Make naive datetimes timezone-aware
                    if start_time and timezone.is_naive(start_time):
                        try:
                            start_time = timezone.make_aware(start_time, assume_tz)
                        except Exception:
                            error_count += 1
                            continue
                    if end_time and timezone.is_naive(end_time):
                        try:
                            end_time = timezone.make_aware(end_time, assume_tz)
                        except Exception:
                            error_count += 1
                            continue

                    if not start_time or not end_time:
                        error_count += 1
                        continue

                    # Get station references
                    initial_station = None
                    final_station = None

                    initial_station_id = None
                    final_station_id = None
                    if pd.notna(row['initial_station_name']):
                        initial_station_id = self.extract_station_id(row['initial_station_name'])
                        if initial_station_id and initial_station_id in station_map:
                            initial_station = station_map[initial_station_id]

                    if pd.notna(row['final_station_name']):
                        final_station_id = self.extract_station_id(row['final_station_name'])
                        if final_station_id and final_station_id in station_map:
                            final_station = station_map[final_station_id]

                    # Filter out trips not related to the desired station_id range
                    if station_id_min is not None or station_id_max is not None:
                        in_range_initial = (
                            initial_station_id is not None
                            and (station_id_min is None or initial_station_id >= station_id_min)
                            and (station_id_max is None or initial_station_id <= station_id_max)
                        )
                        in_range_final = (
                            final_station_id is not None
                            and (station_id_min is None or final_station_id >= station_id_min)
                            and (station_id_max is None or final_station_id <= station_id_max)
                        )
                        # Keep trip only if either end is within range
                        if not (in_range_initial or in_range_final):
                            continue

                    # Create trip object
                    trip = Trip(
                        trip_id=str(row['trip_id']),
                        duration_seconds=int(float(row['duration_seconds'])) if pd.notna(row['duration_seconds']) else 0,
                        initial_station_name=str(row['initial_station_name']) if pd.notna(row['initial_station_name']) else '',
                        final_station_name=str(row['final_station_name']) if pd.notna(row['final_station_name']) else '',
                        initial_station=initial_station,
                        final_station=final_station,
                        start_time=start_time,
                        end_time=end_time,
                        birth_year=str(row['birth_year']) if pd.notna(row['birth_year']) else '',
                        initial_station_latitude=float(row['initial_station_latitude']) if pd.notna(row['initial_station_latitude']) else None,
                        initial_station_longitude=float(row['initial_station_longitude']) if pd.notna(row['initial_station_longitude']) else None,
                        final_station_latitude=float(row['final_station_latitude']) if pd.notna(row['final_station_latitude']) else None,
                        final_station_longitude=float(row['final_station_longitude']) if pd.notna(row['final_station_longitude']) else None,
                        # Pre-compute fields for faster queries
                        start_day=start_time.weekday(),
                        start_hour=start_time.hour,
                        end_day=end_time.weekday(),
                        end_hour=end_time.hour,
                        month=start_time.month,
                    )
                    trip_objects.append(trip)

                    # Respect max cap
                    if max_to_import is not None and (imported_count + len(trip_objects)) >= max_to_import:
                        reached_cap = True
                        break

                except Exception as e:
                    error_count += 1
                    if error_count <= 10:  # Show first 10 errors
                        self.stdout.write(f"    Error processing row: {str(e)}")
                    continue

            # Bulk create trips for this batch
            if trip_objects:
                with transaction.atomic():
                    Trip.objects.bulk_create(trip_objects, ignore_conflicts=True)
                imported_count += len(trip_objects)

        self.stdout.write(f"  ✓ Successfully imported {imported_count} trips from this chunk")
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠ Skipped {error_count} rows due to errors in this chunk"))
        return imported_count

    def count_csv_rows(self, file_path: str) -> int:
        """Return the exact number of data rows in a CSV (excluding header)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
            return max(0, total_lines - 1)
        except Exception:
            return None

    def estimate_total_rows(self, file_path: str, sample_lines: int = 20000) -> int:
        """Estimate the number of data rows by sampling average line length.
        Returns None if estimation fails.
        """
        try:
            file_size = os.path.getsize(file_path)
            if file_size <= 0:
                return None
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                header = f.readline()
                header_len = len(header)
                total_len = 0
                count = 0
                for _ in range(sample_lines):
                    line = f.readline()
                    if not line:
                        break
                    total_len += len(line)
                    count += 1
            if count == 0 or total_len == 0:
                return None
            avg_len = total_len / count
            estimated = int((max(0, file_size - header_len)) / max(1, avg_len))
            return max(1, estimated)
        except Exception:
            return None