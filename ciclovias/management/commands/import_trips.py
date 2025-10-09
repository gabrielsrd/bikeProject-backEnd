from django.core.management.base import BaseCommand
import pandas as pd
from ciclovias.models import Station, Trip
from django.utils.dateparse import parse_datetime
import re
from tqdm import tqdm
from django.db import transaction

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
            # Read CSV file
            self.stdout.write(f"Reading CSV file: {csv_file}")
            if test_run:
                df = pd.read_csv(csv_file, nrows=1000)
                self.stdout.write(self.style.WARNING("TEST RUN: Importing only first 1000 rows"))
            elif limit:
                df = pd.read_csv(csv_file, nrows=limit)
                self.stdout.write(self.style.WARNING(f"LIMITED IMPORT: Importing only first {limit} rows"))
            else:
                df = pd.read_csv(csv_file)
            
            self.stdout.write(f"CSV loaded: {len(df)} rows")
            
            # First pass: Import stations
            self.stdout.write("Phase 1: Importing stations...")
            self.import_stations(df)
            
            # Second pass: Import trips
            self.stdout.write("Phase 2: Importing trips...")
            self.import_trips(df, batch_size)
            
            self.stdout.write(self.style.SUCCESS("Import completed successfully!"))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            raise

    def import_stations(self, df):
        """Import unique stations from the CSV data"""
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
        with transaction.atomic():
            Station.objects.bulk_create(station_objects, ignore_conflicts=True)
        
        self.stdout.write(f"  ✓ Processed {len(station_objects)} unique stations")

    def import_trips(self, df, batch_size):
        """Import trips from CSV in batches"""
        total_rows = len(df)
        imported_count = 0
        error_count = 0
        
        # Create a mapping of station names to Station objects for faster lookup
        station_map = {}
        for station in Station.objects.all():
            if station.station_id:
                station_map[station.station_id] = station
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]
            
            self.stdout.write(f"  Processing batch {start_idx + 1}-{end_idx} of {total_rows}")
            
            trip_objects = []
            for _, row in batch.iterrows():
                try:
                    # Parse timestamps
                    start_time = parse_datetime(str(row['start_time'])) if pd.notna(row['start_time']) else None
                    end_time = parse_datetime(str(row['end_time'])) if pd.notna(row['end_time']) else None
                    
                    if not start_time or not end_time:
                        error_count += 1
                        continue
                    
                    # Get station references
                    initial_station = None
                    final_station = None
                    
                    if pd.notna(row['initial_station_name']):
                        initial_station_id = self.extract_station_id(row['initial_station_name'])
                        if initial_station_id and initial_station_id in station_map:
                            initial_station = station_map[initial_station_id]
                    
                    if pd.notna(row['final_station_name']):
                        final_station_id = self.extract_station_id(row['final_station_name'])
                        if final_station_id and final_station_id in station_map:
                            final_station = station_map[final_station_id]
                    
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
            
        self.stdout.write(f"  ✓ Successfully imported {imported_count} trips")
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠ Skipped {error_count} rows due to errors"))