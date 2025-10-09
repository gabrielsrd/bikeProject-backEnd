#!/usr/bin/env python3
"""
Test script to check API endpoints and debug frontend connection issues
"""
import requests
import json
import sys

def test_endpoint(url, name):
    """Test an API endpoint and display results"""
    print(f"\n🔍 Testing {name}: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Response Size: {len(response.text)} characters")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"JSON Keys: {list(data.keys())}")
                    # Show sample of data
                    for key, value in list(data.items())[:3]:
                        if isinstance(value, (list, dict)):
                            print(f"  {key}: {type(value).__name__} with {len(value)} items")
                        else:
                            print(f"  {key}: {value}")
                elif isinstance(data, list):
                    print(f"JSON Array with {len(data)} items")
                    if data:
                        print(f"First item: {data[0]}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Response is not valid JSON")
                print(f"First 200 chars: {response.text[:200]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - server not running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 API ENDPOINT TESTING")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test different endpoints
    endpoints = [
        (f"{base_url}/api/station_histogram_test/", "Database Endpoint (NEW)"),
        (f"{base_url}/api/station_histogram/", "CSV Endpoint (OLD)"),
        (f"{base_url}/api/station_histogram_test/?start_day=1&end_day=7", "Database with Parameters"),
    ]
    
    results = []
    for url, name in endpoints:
        success = test_endpoint(url, name)
        results.append((name, success))
    
    print(f"\n📊 SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"{status} - {name}")
    
    # Additional debugging info
    print(f"\n🔧 DEBUGGING TIPS:")
    print("- If database endpoint fails, check Django models and migrations")
    print("- If CSV endpoint works but database doesn't, the data migration worked but API has issues")
    print("- Check browser dev tools for CORS errors")
    print("- Verify frontend is using the correct endpoint URL")
    
if __name__ == "__main__":
    main()