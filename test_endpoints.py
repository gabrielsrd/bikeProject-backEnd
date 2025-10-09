#!/usr/bin/env python3
"""
Test script to compare API endpoints - working around terminal issue
"""
import requests
import json
import sys

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    # Test original CSV-based endpoint
    print("Testing original CSV-based endpoint: /api/station_histogram/")
    try:
        # Increase timeout for large CSV processing
        response1 = requests.get(f"{base_url}/api/station_histogram/", timeout=30)
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✓ CSV endpoint works - Status: {response1.status_code}")
            print(f"  Response type: {type(data1)}")
            if isinstance(data1, list):
                print(f"  Number of items: {len(data1)}")
                if data1:
                    print(f"  Sample item: {data1[0]}")
        else:
            print(f"✗ CSV endpoint failed - Status: {response1.status_code}")
            print(f"  Error: {response1.text}")
    except Exception as e:
        print(f"✗ Error testing CSV endpoint: {e}")
        return False
    
    # Test new database-based endpoint
    print("\nTesting new database-based endpoint: /api/station_histogram_test/")
    try:
        response2 = requests.get(f"{base_url}/api/station_histogram_test/", timeout=30)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✓ Database endpoint works - Status: {response2.status_code}")
            print(f"  Response type: {type(data2)}")
            if isinstance(data2, list):
                print(f"  Number of items: {len(data2)}")
                if data2:
                    print(f"  Sample item: {data2[0]}")
        else:
            print(f"✗ Database endpoint failed - Status: {response2.status_code}")
            print(f"  Error: {response2.text}")
    except Exception as e:
        print(f"✗ Error testing database endpoint: {e}")
        return False
    
    # Compare results if both worked
    try:
        if response1.status_code == 200 and response2.status_code == 200:
            print("\n" + "="*50)
            print("COMPARISON RESULTS:")
            print("="*50)
            
            if isinstance(data1, list) and isinstance(data2, list):
                print(f"CSV endpoint items: {len(data1)}")
                print(f"Database endpoint items: {len(data2)}")
                
                if len(data1) == len(data2):
                    print("✓ Same number of items")
                else:
                    print("✗ Different number of items")
                
                # Sample comparison
                if data1 and data2:
                    print(f"\nSample CSV item keys: {list(data1[0].keys()) if data1[0] else 'No keys'}")
                    print(f"Sample DB item keys: {list(data2[0].keys()) if data2[0] else 'No keys'}")
            else:
                print(f"Data types - CSV: {type(data1)}, DB: {type(data2)}")
        
        return True
        
    except Exception as e:
        print(f"Error comparing results: {e}")
        return False

if __name__ == '__main__':
    success = test_endpoints()
    sys.exit(0 if success else 1)