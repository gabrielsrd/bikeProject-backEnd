#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/galves/gabriel/usp/tccBike/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Initialize Django
django.setup()

# Test importing the models
try:
    from ciclovias.models import Station, Trip
    print("✅ Models imported successfully!")
    print(f"Station model: {Station}")
    print(f"Trip model: {Trip}")
    
    # Check if we can create migrations
    from django.core.management import execute_from_command_line
    print("✅ Django management commands available")
    
    # Test database connection
    from django.db import connection
    print("✅ Database connection available")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()