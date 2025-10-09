#!/usr/bin/env python3
"""
Simple test for database endpoint only
"""
import requests
import json

def test_db_endpoint():
    print("Testing database endpoint: /api/station_histogram_test/")
    try:
        response = requests.get("http://127.0.0.1:8000/api/station_histogram_test/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Got {len(data)} items")
            
            if data:
                print(f"Sample item: {data[0]}")
                print(f"Sample keys: {list(data[0].keys())}")
                
                # Quick validation
                print("\nData validation:")
                print(f"- Total items: {len(data)}")
                if 'station_id' in data[0]:
                    unique_stations = len(set(item['station_id'] for item in data))
                    print(f"- Unique stations: {unique_stations}")
                if 'count' in data[0]:
                    total_trips = sum(item['count'] for item in data)
                    print(f"- Total trip count: {total_trips}")
            
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    test_db_endpoint()