# TCC Bike Backend - Project Reorganization Plan

## Project Overview
This is a Django backend for a shared bike trip analysis system, part of a TCC (thesis) project. The frontend will be a map showing bike trip information and patterns.

## Current Structure Analysis
- **Django Project**: Already setup with `myproject` and `ciclovias` app
- **Large Dataset**: Consolidated Tembici bike trip data (~50MB+ CSV)
- **Geospatial Data**: GeoJSON files for bike lanes and stations
- **Data Processing Scripts**: Python scripts for data extraction and consolidation

## 📋 REORGANIZATION PLAN

### Phase 1: Project Structure Cleanup
```
bikeProject-backEnd/
├── apps/                          # Django apps
│   ├── trips/                     # Bike trips management
│   ├── stations/                  # Bike stations
│   ├── ciclovias/                 # Bike lanes (existing)
│   └── analytics/                 # Data analytics endpoints
├── config/                        # Django configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── data/                          # Data management
│   ├── raw/                       # Raw data (gitignored)
│   ├── processed/                 # Processed data
│   ├── imports/                   # Data import scripts
│   └── fixtures/                  # Django fixtures
├── static/                        # Static files
├── media/                         # Media files
├── requirements/                  # Dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docs/                          # Documentation
├── tests/                         # Test files
├── docker/                        # Docker configuration
├── scripts/                       # Utility scripts
└── manage.py
```

### Phase 2: Database Schema Design
Create Django models for:

1. **Station Model**
   - id, name, latitude, longitude
   - address, capacity, status
   - created_at, updated_at

2. **Trip Model**
   - trip_id, duration_seconds
   - start_station (FK), end_station (FK)
   - start_time, end_time
   - birth_year (optional)
   - created_at

3. **Ciclovia Model** (bike lanes)
   - name, description
   - geometry (GeoJSON)
   - type, status

4. **Analytics Models**
   - HourlyStats, DailyStats
   - StationUsage, PopularRoutes

### Phase 3: Data Migration Strategy
1. **SQLite to PostgreSQL** (recommended for geospatial data)
   - Better performance for large datasets
   - PostGIS extension for geospatial queries
   - Better JSON support

2. **Data Import Pipeline**
   - Convert CSV to Django models
   - Batch processing for large datasets
   - Data validation and cleaning
   - Progress tracking

### Phase 4: API Development
1. **REST API Endpoints**
   - `/api/trips/` - Trip CRUD operations
   - `/api/stations/` - Station information
   - `/api/ciclovias/` - Bike lanes
   - `/api/analytics/` - Analytics data

2. **Geospatial Endpoints**
   - `/api/trips/heatmap/` - Trip density
   - `/api/stations/nearby/` - Nearby stations
   - `/api/routes/popular/` - Popular routes

### Phase 5: Performance Optimization
1. **Database Indexing**
   - Geospatial indexes
   - Time-based indexes
   - Station foreign key indexes

2. **Caching Strategy**
   - Redis for analytics data
   - Cache expensive queries
   - API response caching

3. **Data Pagination**
   - Efficient pagination for large datasets
   - Cursor-based pagination for time series

## 🗄️ DATABASE CONVERSION PLAN

### Option 1: PostgreSQL + PostGIS (Recommended)
**Pros:**
- Excellent geospatial support
- Better performance for large datasets
- JSON/JSONB support
- Full-text search capabilities

**Implementation:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bike_tcc',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Option 2: Optimized SQLite (Current + Improvements)
**Pros:**
- No additional setup
- Good for development
- Easier deployment

**Improvements:**
- Enable WAL mode
- Create proper indexes
- Use Django's bulk operations

## 🚀 IMPLEMENTATION PRIORITY

### Phase 1 (Immediate - Week 1)
1. ✅ Reorganize project structure
2. ✅ Create proper Django models
3. ✅ Setup database migrations
4. ✅ Import consolidated trip data

### Phase 2 (Week 2)
1. ✅ Create REST API endpoints
2. ✅ Add data validation
3. ✅ Setup basic analytics
4. ✅ Add geospatial queries

### Phase 3 (Week 3)
1. ✅ Performance optimization
2. ✅ Add caching
3. ✅ Frontend integration
4. ✅ Documentation

### Phase 4 (Week 4)
1. ✅ Testing
2. ✅ Deployment setup
3. ✅ Final optimizations

## 📊 DATA CONVERSION STRATEGY

### For Large CSV Data (50M+ rows):
1. **Chunked Processing**: Process data in batches of 10,000 rows
2. **Background Tasks**: Use Celery for long-running imports
3. **Progress Tracking**: Show import progress
4. **Memory Management**: Use iterators instead of loading all data

### Sample Import Script:
```python
def import_trips_from_csv(csv_file, batch_size=10000):
    for chunk in pd.read_csv(csv_file, chunksize=batch_size):
        trip_objects = []
        for _, row in chunk.iterrows():
            trip_objects.append(Trip(
                trip_id=row['trip_id'],
                duration_seconds=row['duration_seconds'],
                # ... other fields
            ))
        Trip.objects.bulk_create(trip_objects, ignore_conflicts=True)
```

## 🔧 NEXT STEPS

1. **Confirm this plan** - Does this structure work for your TCC requirements?
2. **Choose database** - PostgreSQL or optimized SQLite?
3. **Start implementation** - Begin with Phase 1?

Would you like me to start implementing any specific part of this plan?