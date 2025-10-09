#!/bin/bash

# Docker Development Helper Script

set -e

echo "🐳 Django Docker Development Helper"
echo "=================================="

case "$1" in
    "build")
        echo "🔨 Building Docker containers..."
        docker compose build
        ;;
    "up")
        echo "🚀 Starting services..."
        docker compose up
        ;;
    "up-d")
        echo "🚀 Starting services in background..."
        docker compose up -d
        ;;
    "down")
        echo "🛑 Stopping services..."
        docker compose down
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker compose logs -f web
        ;;
    "shell")
        echo "🐚 Opening Django shell..."
        docker compose exec web python manage.py shell
        ;;
    "migrate")
        echo "🗃️ Running migrations..."
        docker compose exec web python manage.py makemigrations
        docker compose exec web python manage.py migrate
        ;;
    "test")
        echo "🧪 Testing API endpoints..."
        echo "CSV endpoint: http://localhost:8000/api/station_histogram/"
        echo "DB endpoint: http://localhost:8000/api/station_histogram_test/"
        curl -s "http://localhost:8000/api/station_histogram_test/" | jq 'length' || echo "jq not installed - install with: apt install jq"
        ;;
    "import")
        echo "📊 Importing trip data..."
        docker compose exec web python manage.py import_trips dataClean/consolidated_tembici_trips.csv --test-run
        ;;
    "import-full")
        echo "📊 Importing FULL trip data..."
        docker compose exec web python manage.py import_trips dataClean/consolidated_tembici_trips.csv
        ;;
    "reset-db")
        echo "🗑️ Resetting database..."
        docker compose exec web rm -f db.sqlite3
        docker compose exec web python manage.py makemigrations ciclovias
        docker compose exec web python manage.py migrate
        ;;
    *)
        echo "Usage: $0 {build|up|up-d|down|logs|shell|migrate|test|import|import-full|reset-db}"
        echo ""
        echo "Commands:"
        echo "  build      - Build Docker containers"
        echo "  up         - Start services (foreground)"
        echo "  up-d       - Start services (background)"
        echo "  down       - Stop services"
        echo "  logs       - Show application logs"
        echo "  shell      - Open Django shell"
        echo "  migrate    - Run database migrations"
        echo "  test       - Test API endpoints"
        echo "  import     - Import test data (1000 rows)"
        echo "  import-full- Import full dataset"
        echo "  reset-db   - Reset SQLite database"
        exit 1
        ;;
esac