#!/bin/bash

echo "🚲 Starting Bike Project Backend"
echo "================================"

# Navigate to project directory
cd /home/galves/gabriel/usp/tccBike/bikeProject-backEnd

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv-1/bin/activate

# Check database
echo "🗃️ Checking database..."
python -c "
import sqlite3
import os
if os.path.exists('db.sqlite3'):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ciclovias_trip;')
    trips = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM ciclovias_station;')
    stations = cursor.fetchone()[0]
    print(f'   ✅ Database ready: {trips:,} trips, {stations} stations')
    conn.close()
else:
    print('   ⚠️ Database not found - run migrations first')
"

# Start Django server
echo "🚀 Starting Django server..."
echo "   Server will be available at: http://localhost:8000"
echo "   Database API: http://localhost:8000/api/station_histogram_test/"
echo "   Press Ctrl+C to stop"
echo ""

python manage.py runserver 8000