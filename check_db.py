#!/usr/bin/env python3
"""
Check database contents
"""
import subprocess
import sys
import os

# Change to project directory
os.chdir('/home/galves/gabriel/usp/tccBike/bikeProject-backEnd')

# Use Django shell to check database
django_shell_code = '''
from ciclovias.models import Trip, Station

print("=== DATABASE ANALYSIS ===")
print(f"Total trips in database: {Trip.objects.count()}")
print(f"Total stations in database: {Station.objects.count()}")

if Trip.objects.exists():
    sample_trip = Trip.objects.first()
    print(f"\\nSample trip:")
    print(f"- Start station: {sample_trip.start_station_id}")
    print(f"- End station: {sample_trip.end_station_id}")
    print(f"- Start time: {sample_trip.start_time}")
    print(f"- End time: {sample_trip.end_time}")

if Station.objects.exists():
    sample_station = Station.objects.first()
    print(f"\\nSample station:")
    print(f"- ID: {sample_station.station_id}")
    print(f"- Name: {sample_station.name}")
    print(f"- Lat: {sample_station.latitude}")
    print(f"- Lon: {sample_station.longitude}")

print(f"\\nUnique start stations in trips: {Trip.objects.values('start_station_id').distinct().count()}")
print(f"Unique end stations in trips: {Trip.objects.values('end_station_id').distinct().count()}")
'''

# Run the Django shell command
result = subprocess.run([
    sys.executable, 'manage.py', 'shell', '-c', django_shell_code
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)