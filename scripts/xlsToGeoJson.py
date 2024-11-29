import json
import folium

import os
import pandas as pd

pathFile =" ../dataRaw/estacoes.xlsx"

df = pd.read_excel(pathFile, engine='openpyxl')

# df["NOME"] = df["NOME"].apply(lambda x: x.encode('latin').decode('utf-8') if isinstance(x, str) else x)

# List to store coordinates
features = []

# change it to use cleaned data from 
for index, row in df.iterrows():
    try :
        point = {}
        point['name'] = row["NOME"]
        latitude = row["LATITUDE (SIG 4326)"]
        longitude = row["LONGITUDE (SIG 4326)"]
        if pd.isnull(latitude) or pd.isnull(longitude):
            continue
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['LONGITUDE (SIG 4326)'], row['LATITUDE (SIG 4326)']]
            },
            "properties": {
                "name": row["NOME"],
                "id": row["NÚMERO ESTAÇÃO"]
                }
        }
        features.append(feature)
        
            
       
        
    
    except :
        print("Error in row: ", row)
    
geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }    
    
#save the geojson data

# print(geojson_data)
with open('estacoes.geojson', 'w') as f:
    f.write(json.dumps(geojson_data, indent=4,  ensure_ascii=False))


