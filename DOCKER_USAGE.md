# Docker Setup for bikeProject Backend

## Quick Start

The easiest way to run the backend with Docker:

```bash
./docker-start.sh
```

Or manually:

```bash
docker-compose -f docker-compose.sqlite.yml up --build
```

## What This Does

1. **Builds a Docker image** with Python 3.12 and all dependencies from `requirements.txt`
2. **Runs database migrations** automatically on startup
3. **Starts the Django development server** on `0.0.0.0:8000`
4. **Persists the SQLite database** (`db.sqlite3`) on your host machine

## Database Persistence

The `db.sqlite3` file is stored in your project directory and mounted into the container. This means:
- ✅ Your data persists when you stop/restart containers
- ✅ You can back up the database by copying `db.sqlite3`
- ✅ You can view/edit the database from your host machine using SQLite tools

## Available Endpoints

Once running, access:
- **Ciclovias:** http://localhost:8000/api/ciclovias/
- **Estações:** http://localhost:8000/api/estacoes/
- **Hotzones:** http://localhost:8000/api/hotzones/

## Useful Commands

### Start in background (detached mode)
```bash
docker-compose -f docker-compose.sqlite.yml up -d
```

### View logs
```bash
docker-compose -f docker-compose.sqlite.yml logs -f
```

### Stop the server
```bash
docker-compose -f docker-compose.sqlite.yml down
```

### Rebuild after code changes
```bash
docker-compose -f docker-compose.sqlite.yml up --build
```

### Run Django management commands
```bash
docker-compose -f docker-compose.sqlite.yml exec backend python manage.py <command>
```

Examples:
```bash
# Create superuser
docker-compose -f docker-compose.sqlite.yml exec backend python manage.py createsuperuser

# Run migrations manually
docker-compose -f docker-compose.sqlite.yml exec backend python manage.py migrate

# Open Django shell
docker-compose -f docker-compose.sqlite.yml exec backend python manage.py shell
```

## Troubleshooting

### Port 8000 already in use
If you get a port conflict, either:
1. Stop the process using port 8000: `lsof -ti:8000 | xargs kill -9`
2. Or edit `docker-compose.sqlite.yml` and change `"8000:8000"` to `"8001:8000"`, then access at http://localhost:8001

### Permission errors with db.sqlite3
If you get database permission errors, check the file permissions:
```bash
ls -la db.sqlite3
chmod 664 db.sqlite3  # Make it readable/writable
```

### Container won't start
View detailed logs:
```bash
docker-compose -f docker-compose.sqlite.yml logs
```

## Development vs Production

This setup is for **development only**. For production:
- Use a proper database (PostgreSQL)
- Use a production WSGI server (Gunicorn)
- Set `DEBUG=False`
- Configure proper security settings
- Use environment variables for secrets

See the existing `docker-compose.yml` for a PostgreSQL setup example.
