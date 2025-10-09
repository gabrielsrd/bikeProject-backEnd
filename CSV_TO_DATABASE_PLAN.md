# CSV to Database Migration Plan - Maintaining All Existing Features

## 🎯 **Goal**: Convert CSV data to SQLite while keeping ALL current API endpoints working

## 📊 **Current API Analysis**

### Existing Working Endpoints:
1. **`/api/ciclostation/`** - GeoJSON from `geojsons/estacoes.geojson` ✅
2. **`/api/ciclovias/`** - GeoJSON from `geojsons/ciclovia.geojson` ✅  
3. **`/api/hotzones/`** - GeoJSON from `geojsons/hotzones.geojson` ✅
4. **`/api/stations/`** - GeoJSON from `geojsons/stations.geojson` ✅
5. **`/api/hourly_counts/`** - JSON from `geojsons/hourly_counts.json` ✅
6. **`/api/station_histogram/`** - **PROCESSES CSV ON-THE-FLY** ⚠️ (This needs database conversion)

### Critical: StationsHistogramAPIView
This endpoint reads `dataRaw/userTrips.csv` and does complex filtering:
- Day filtering (weekdays/weekends)
- Month exclusion
- Station ID filtering  
- USP station filtering (242-260)
- Hourly departure/arrival counts

## 🔄 **Migration Strategy - Phase by Phase**

### **Phase 1: Create Models (Keep CSV as backup)**
Create Django models that match your consolidated CSV structure while keeping existing CSV processing as fallback.

### **Phase 2: Import Data to Database**
Convert your consolidated CSV to database tables using efficient bulk operations.

### **Phase 3: Update Views (Gradual Migration)**
Replace CSV processing with database queries, one endpoint at a time.

### **Phase 4: Performance Optimization**
Add indexes and optimize queries for your frontend needs.

---

## 📝 **DETAILED IMPLEMENTATION PLAN**

### **STEP 1: Create Django Models**

```python
# ciclovias/models.py
from django.db import models
from django.core.validators import MinValueValidator

class Station(models.Model):
    station_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['station_id']),
            models.Index(fields=['name']),
        ]

class Trip(models.Model):
    trip_id = models.CharField(max_length=255, unique=True)
    duration_seconds = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Station references
    initial_station_name = models.CharField(max_length=255)
    final_station_name = models.CharField(max_length=255)
    initial_station = models.ForeignKey(Station, on_delete=models.SET_NULL, 
                                      null=True, related_name='departing_trips')
    final_station = models.ForeignKey(Station, on_delete=models.SET_NULL, 
                                    null=True, related_name='arriving_trips')
    
    # Timestamps
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Additional data
    birth_year = models.CharField(max_length=10, blank=True)
    
    # Coordinates (for trips without station references)
    initial_station_latitude = models.FloatField(null=True, blank=True)
    initial_station_longitude = models.FloatField(null=True, blank=True)
    final_station_latitude = models.FloatField(null=True, blank=True)
    final_station_longitude = models.FloatField(null=True, blank=True)
    
    # Computed fields for faster queries
    start_day = models.IntegerField(null=True, blank=True)  # 0=Mon, 6=Sun
    start_hour = models.IntegerField(null=True, blank=True)
    end_day = models.IntegerField(null=True, blank=True)
    end_hour = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['start_day']),
            models.Index(fields=['start_hour']),
            models.Index(fields=['month']),
            models.Index(fields=['initial_station']),
            models.Index(fields=['final_station']),
        ]
```

### **STEP 2: Create Data Import Management Command**

```python
# ciclovias/management/commands/import_trips.py
from django.core.management.base import BaseCommand
import pandas as pd
from ciclovias.models import Station, Trip
from django.utils.dateparse import parse_datetime
import re
from tqdm import tqdm

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to consolidated CSV file')
        parser.add_argument('--batch-size', type=int, default=5000, 
                          help='Batch size for bulk operations')

    def extract_station_id(self, name):
        if not isinstance(name, str):
            return None
        match = re.search(r'(\d+)', name)
        return int(match.group(1)) if match else None

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        
        self.stdout.write("Starting CSV import...")
        
        # First pass: Import stations
        self.stdout.write("Importing stations...")
        df = pd.read_csv(csv_file)
        
        stations_data = set()
        for _, row in df.iterrows():
            for station_type in ['initial', 'final']:
                name = row[f'{station_type}_station_name']
                lat = row[f'{station_type}_station_latitude']
                lon = row[f'{station_type}_station_longitude']
                
                if pd.notna(name):
                    station_id = self.extract_station_id(name)
                    stations_data.add((
                        station_id, name, 
                        lat if pd.notna(lat) else None,
                        lon if pd.notna(lon) else None
                    ))
        
        # Bulk create stations
        station_objects = []
        for station_id, name, lat, lon in stations_data:
            station_objects.append(Station(
                station_id=station_id,
                name=name,
                latitude=lat,
                longitude=lon
            ))
        
        Station.objects.bulk_create(station_objects, ignore_conflicts=True)
        self.stdout.write(f"Created {len(station_objects)} stations")
        
        # Second pass: Import trips in batches
        self.stdout.write("Importing trips...")
        total_rows = len(df)
        
        for start_idx in tqdm(range(0, total_rows, batch_size), desc="Processing batches"):
            end_idx = min(start_idx + batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]
            
            trip_objects = []
            for _, row in batch.iterrows():
                try:
                    start_time = parse_datetime(row['start_time'])
                    end_time = parse_datetime(row['end_time'])
                    
                    # Get station references
                    initial_station = None
                    final_station = None
                    
                    if pd.notna(row['initial_station_name']):
                        initial_station_id = self.extract_station_id(row['initial_station_name'])
                        if initial_station_id:
                            try:
                                initial_station = Station.objects.get(station_id=initial_station_id)
                            except Station.DoesNotExist:
                                pass
                    
                    if pd.notna(row['final_station_name']):
                        final_station_id = self.extract_station_id(row['final_station_name'])
                        if final_station_id:
                            try:
                                final_station = Station.objects.get(station_id=final_station_id)
                            except Station.DoesNotExist:
                                pass
                    
                    trip = Trip(
                        trip_id=row['trip_id'],
                        duration_seconds=int(row['duration_seconds']) if pd.notna(row['duration_seconds']) else 0,
                        initial_station_name=row['initial_station_name'] if pd.notna(row['initial_station_name']) else '',
                        final_station_name=row['final_station_name'] if pd.notna(row['final_station_name']) else '',
                        initial_station=initial_station,
                        final_station=final_station,
                        start_time=start_time,
                        end_time=end_time,
                        birth_year=row['birth_year'] if pd.notna(row['birth_year']) else '',
                        initial_station_latitude=row['initial_station_latitude'] if pd.notna(row['initial_station_latitude']) else None,
                        initial_station_longitude=row['initial_station_longitude'] if pd.notna(row['initial_station_longitude']) else None,
                        final_station_latitude=row['final_station_latitude'] if pd.notna(row['final_station_latitude']) else None,
                        final_station_longitude=row['final_station_longitude'] if pd.notna(row['final_station_longitude']) else None,
                        # Computed fields
                        start_day=start_time.weekday() if start_time else None,
                        start_hour=start_time.hour if start_time else None,
                        end_day=end_time.weekday() if end_time else None,
                        end_hour=end_time.hour if end_time else None,
                        month=start_time.month if start_time else None,
                    )
                    trip_objects.append(trip)
                    
                except Exception as e:
                    self.stdout.write(f"Error processing row: {e}")
                    continue
            
            # Bulk create trips
            Trip.objects.bulk_create(trip_objects, ignore_conflicts=True)
            
        self.stdout.write(f"Successfully imported {total_rows} trips")
```

### **STEP 3: Update StationsHistogramAPIView (Database Version)**

```python
# New database-powered version
class StationsHistogramAPIView(APIView):
    def get(self, request):
        from django.db.models import Count, Q
        from ciclovias.models import Trip
        
        # Get query parameters (same as before)
        selected_days = request.query_params.get('days', None) 
        exclude_months = request.query_params.get('months', None) 
        station_id = request.query_params.get('station_id', None) 
        usp = request.query_params.get('usp', None) 
        
        # Start with all trips
        queryset = Trip.objects.all()
        
        # Filter by days
        if selected_days:
            try:
                selected_days = [int(day) for day in selected_days.split(',')]
                queryset = queryset.filter(start_day__in=selected_days)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'days' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to weekdays
            queryset = queryset.filter(start_day__lt=5)
        
        # Filter by excluded months
        if exclude_months:
            try:
                exclude_months = [int(month) for month in exclude_months.split(',')]
                queryset = queryset.exclude(month__in=exclude_months)
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'months' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter by station_id
        if station_id:
            try:
                station_id = int(station_id)
                queryset = queryset.filter(
                    Q(initial_station__station_id=station_id) | 
                    Q(final_station__station_id=station_id)
                )
            except (ValueError, TypeError):
                return Response({"error": "Invalid 'station_id' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter by USP stations (242-260)
        if usp and usp.lower() == 'true':
            usp_range = range(242, 261)
            queryset = queryset.filter(
                Q(initial_station__station_id__in=usp_range) | 
                Q(final_station__station_id__in=usp_range)
            )
        
        # Get departures and arrivals data
        departures = queryset.values(
            'initial_station_name', 
            'initial_station__station_id', 
            'start_day', 
            'start_hour'
        ).annotate(departures=Count('id'))
        
        arrivals = queryset.values(
            'final_station_name', 
            'final_station__station_id', 
            'end_day', 
            'end_hour'
        ).annotate(arrivals=Count('id'))
        
        # Convert to the same JSON format as before
        histogram_data = {}
        
        # Process departures
        for item in departures:
            key = (item['initial_station__station_id'], item['start_day'], item['start_hour'])
            if key not in histogram_data:
                histogram_data[key] = {
                    'station_id': item['initial_station__station_id'],
                    'station': item['initial_station_name'],
                    'day': item['start_day'],
                    'hour': item['start_hour'],
                    'departures': 0,
                    'arrivals': 0
                }
            histogram_data[key]['departures'] = item['departures']
        
        # Process arrivals
        for item in arrivals:
            key = (item['final_station__station_id'], item['end_day'], item['end_hour'])
            if key not in histogram_data:
                histogram_data[key] = {
                    'station_id': item['final_station__station_id'],
                    'station': item['final_station_name'],
                    'day': item['end_day'],
                    'hour': item['end_hour'],
                    'departures': 0,
                    'arrivals': 0
                }
            histogram_data[key]['arrivals'] = item['arrivals']
        
        return Response(list(histogram_data.values()), status=status.HTTP_200_OK)
```

---

## 🚀 **EXECUTION STEPS**

### **Step 1: Create Models and Migrate**
```bash
# Add models to ciclovias/models.py
python manage.py makemigrations ciclovias
python manage.py migrate
```

### **Step 2: Import Your Consolidated CSV**
```bash
# Create the import command and run it
python manage.py import_trips dataClean/consolidated_tembici_trips.csv
```

### **Step 3: Test Database Version**
- Keep the old CSV version as backup
- Add a new endpoint `/api/station_histogram_db/` with database version
- Test that it returns the same results as CSV version

### **Step 4: Switch Over**
- Replace the CSV version with database version
- Monitor performance

---

## ✅ **VALIDATION CHECKLIST**

### Before Implementation:
- [ ] Backup current working code
- [ ] Confirm CSV file location and format
- [ ] Test that all current endpoints work

### After Models Creation:
- [ ] Database tables created successfully
- [ ] Can import small sample of CSV data
- [ ] Foreign key relationships work

### After Full Import:
- [ ] All CSV data imported correctly
- [ ] Database queries return same results as CSV processing
- [ ] Performance is acceptable for frontend

### After View Updates:
- [ ] All API endpoints return identical JSON
- [ ] Frontend still works perfectly
- [ ] No breaking changes

---

## 📋 **QUESTIONS FOR YOU**

1. **Ready to start?** Should I begin with Step 1 (creating the models)?

2. **CSV file location?** Is your consolidated CSV at `dataClean/consolidated_tembici_trips.csv`?

3. **Testing strategy?** Want me to create a test endpoint first so we can compare CSV vs Database results?

4. **Backup plan?** Should I create a feature flag to switch between CSV and database processing?

This plan ensures ZERO downtime and maintains ALL existing functionality. We can test each step thoroughly before moving to the next.