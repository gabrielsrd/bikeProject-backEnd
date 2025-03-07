import json
import folium
import os
import pandas as pd
import geopandas as gpd

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

# Carregar o arquivo CSV
csv_file = "../dataRaw/userTrips.csv"
df_trips = pd.read_csv(csv_file)

# Calcular o número de entradas e saídas por estação
station_counts = df_trips.groupby('initial_station_name').size().reset_index(name='departures')
station_counts = station_counts.merge(df_trips.groupby('final_station_name').size().reset_index(name='arrivals'), left_on='initial_station_name', right_on='final_station_name', how='outer').fillna(0)
station_counts['total'] = station_counts['departures'] + station_counts['arrivals']

# Criar um GeoDataFrame com as estações e suas contagens
stations = df[['NOME', 'LATITUDE (SIG 4326)', 'LONGITUDE (SIG 4326)']].drop_duplicates()
stations = stations.merge(station_counts, left_on='NOME', right_on='initial_station_name', how='left')
stations_gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations['LONGITUDE (SIG 4326)'], stations['LATITUDE (SIG 4326)']))

# Salvar o GeoJSON com as estações e suas contagens
stations_gdf.to_file('stations_with_counts.geojson', driver='GeoJSON')


