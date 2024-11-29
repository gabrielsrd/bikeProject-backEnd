import folium
from geopy.geocoders import Nominatim

# Initialize geolocator
geolocator = Nominatim(user_agent="geopiMac")

# Addresses to geocode
addresses = [
    "Empire State Building, New York, NY",
    "Hollywood Sign, Los Angeles, CA",
    "Golden Gate Bridge, San Francisco, CA",
]

# List to store coordinates
points = []

# Geocode addresses
for address in addresses:
    location = geolocator.geocode(address)
    if location:
        points.append({'lat': location.latitude, 'lon': location.longitude, 'name': address})

print('pontos', points)
# Initialize a map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # Center map on the USA

# Add points to the map
for point in points:
    folium.Marker(
        location=[point['lat'], point['lon']],
        popup=point['name']
    ).add_to(m)

# Save the map to an HTML file
m.save('map.html')