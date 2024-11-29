import folium
from geopy.geocoders import Nominatim

import os
import pandas as pd

pathFile = "../dataRaw/estacoes.xlsx"

# read the xlsx file
df = pd.read_excel(pathFile)


# Initialize geolocator
geolocator = Nominatim(user_agent="geopiTembiciStations")

# List to store coordinates
points = []


# change it to use cleaned data from 
for index, row in df.iterrows():
    try :
        point = {}
        point['name'] = row["NOME"]
        latitude = row["LATITUDE (SIG 4326)"]
        longitude = row["LONGITUDE (SIG 4326)"]
        #check if the latitude and longitude are not null
        if pd.isnull(latitude) or pd.isnull(longitude):
            address = row["ENDEREÇO "]
            location = geolocator.geocode(address)
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                print("Could not geocode address: ", address)
                continue
            
        point['lat'] = latitude
        point['lon'] = longitude
        
    
    except :
        print("Error in row: ", row)
    
    points.append(point)
    

# Initialize a map
m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12)  # Center map on São Paulo

# print(points)
# Add points to the map
for point in points:
    folium.Marker(
        location=[point['lat'], point['lon']],
        popup=point['name']
    ).add_to(m)
    
m.save('mapEstacoesTembici.html')

#To print the trajectory, we will use poly line from folium