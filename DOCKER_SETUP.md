# Django Backend Docker Setup

This Docker setup provides a clean, consistent environment for the Django backend with all dependencies properly managed.

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose (newer `docker compose` command)

### Setup and Run

1. **Build the containers:**
   ```bash
   docker compose build
   ```

2. **Start the services:**
   ```bash
   docker compose up
   ```
   
   Or in background:
   ```bash
   docker compose up -d
   ```

3. **Access the application:**
   - Django API: http://localhost:8000
   - CSV endpoint: http://localhost:8000/api/station_histogram/
   - Database endpoint: http://localhost:8000/api/station_histogram_test/

### 📊 Data Import

Import test data (1000 rows):
```bash
docker compose exec web python manage.py import_trips dataClean/consolidated_tembici_trips.csv --test-run
```

Import full dataset:
```bash
docker compose exec web python manage.py import_trips dataClean/consolidated_tembici_trips.csv
```

### 🛠️ Development Commands

**Database operations:**
```bash
# Run migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Reset database
docker compose exec web rm -f db.sqlite3
docker compose exec web python manage.py migrate
```

**Debugging:**
```bash
# View logs
docker compose logs -f web

# Open Django shell
docker compose exec web python manage.py shell

# Access container bash
docker compose exec web bash
```

**Stop services:**
```bash
docker compose down
```

## 🗃️ Database Configuration

Currently configured for SQLite (for easy development). To switch to PostgreSQL:

1. Update `.env` file (copy from `.env.example`)
2. Change `DATABASE_URL` to PostgreSQL format
3. Restart containers

## 📁 Project Structure

```
bikeProject-backEnd/
├── Dockerfile              # Django container definition
├── docker-compose.yml      # Multi-service setup
├── requirements.txt         # Python dependencies
├── docker-dev.sh          # Development helper script
├── .dockerignore           # Files to exclude from Docker build
└── .env.example           # Environment configuration template
```

## ✅ Validation Steps

After starting the containers:

1. **Check server status:**
   ```bash
   curl http://localhost:8000/api/station_histogram_test/
   ```

2. **Compare endpoints:**
   - CSV processing: Large response (~2.3MB), slower
   - Database processing: Fast response, fewer records (test data)

3. **Import full data and retest for performance comparison**

## 🔄 Migration from Local Development

The Docker setup maintains compatibility with existing:
- Database structure (SQLite `db.sqlite3`)
- API endpoints
- Data files in `dataClean/` and `geojsons/`
- Frontend integration (same URLs)

All environment issues are resolved within the container!