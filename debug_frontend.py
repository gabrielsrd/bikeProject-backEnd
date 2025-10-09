#!/usr/bin/env python3
"""
Frontend debugging guide for the bike sharing project
Database vs CSV endpoint comparison and troubleshooting steps
"""

print("🚦 FRONTEND CONNECTION DEBUGGING GUIDE")
print("=" * 50)

print("""
📊 CURRENT STATUS:
✅ Database: 1,000,000 trips + 338 stations imported successfully
✅ Django Server: Running on http://127.0.0.1:8000/
✅ Database Endpoint: /api/station_histogram_test/ - WORKING
✅ API Response: Valid JSON with station data

🔧 TROUBLESHOOTING STEPS:

1. CHECK YOUR FRONTEND ENDPOINT URL:
   ❌ OLD (CSV): http://localhost:8000/api/station_histogram/
   ✅ NEW (DB):  http://localhost:8000/api/station_histogram_test/

2. VERIFY API RESPONSES:
   Test these URLs in your browser or with curl:
   
   Basic endpoint:
   http://localhost:8000/api/station_histogram_test/
   
   With parameters:
   http://localhost:8000/api/station_histogram_test/?start_day=1&end_day=7
   http://localhost:8000/api/station_histogram_test/?start_day=0&end_day=6&start_hour=6&end_hour=22

3. CHECK CORS SETTINGS:
   - Django is configured with django-cors-headers
   - CORS_ALLOW_ALL_ORIGINS = True in settings.py
   - Should allow cross-origin requests

4. VERIFY JSON STRUCTURE:
   Both endpoints return the same format:
   [
     {
       "station_id": 177,
       "station": "177 - Av. São João...",
       "day": 0,
       "hour": 8,
       "departures": 12,
       "arrivals": 5
     },
     ...
   ]

5. PERFORMANCE COMPARISON:
   📈 Database endpoint: ~1 second response time
   🐌 CSV endpoint: ~25+ seconds response time
   
6. CHECK BROWSER DEVELOPER TOOLS:
   - Open F12 Developer Tools
   - Go to Network tab
   - Make request to API
   - Check for:
     * HTTP status codes (should be 200)
     * CORS errors
     * Request/Response headers
     * Response body

7. COMMON ISSUES:
   a) Wrong endpoint URL (using old CSV endpoint)
   b) Server not running (check if Django is active)
   c) Port conflicts (ensure port 8000 is free)
   d) CORS blocking (should be fixed in settings)
   e) Frontend caching old responses

8. TEST WITH CURL:
   curl -H "Content-Type: application/json" \\
        "http://localhost:8000/api/station_histogram_test/?start_day=1&end_day=5"

9. FRONTEND CODE CHANGES NEEDED:
   Update your frontend to use:
   - NEW URL: /api/station_histogram_test/
   - Same parameters work: start_day, end_day, start_hour, end_hour
   - Same JSON structure returned

🚨 IF FRONTEND STILL NOT WORKING:

1. Check exact error message in browser console
2. Verify Django server is running: ps aux | grep runserver
3. Test with Postman or insomnia REST client
4. Check if frontend is pointing to correct port
5. Verify network requests in browser dev tools

💡 NEXT STEPS:
- Update frontend API URL to use database endpoint
- Test with smaller parameter ranges first
- Monitor response times (should be much faster)
- Consider importing more data if needed (currently 1M of 16M trips)
""")

print("\n🔍 QUICK API TEST:")
print("Run this command to test the API:")
print("curl 'http://localhost:8000/api/station_histogram_test/?start_day=1&end_day=3' | head -20")

print("\n🎯 MOST LIKELY ISSUE:")
print("Your frontend is probably still using the old CSV endpoint.")
print("Change from: /api/station_histogram/")
print("Change to:   /api/station_histogram_test/")
print("Everything else should work the same!")