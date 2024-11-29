import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import geopandas as gpd
from shapely.geometry import Point
import json

# Carregar o arquivo CSV
csv_file = "../dataRaw/userTrips.csv" 
df = pd.read_csv(csv_file)

# Filtra as colunas de interesse (coordenadas de origem e destino)
df = df[['initial_station_latitude', 'initial_station_longitude', 'final_station_latitude', 'final_station_longitude']]

df = df.dropna(subset=['initial_station_latitude', 'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'])

# Coleta todas as coordenadas (origem e destino) em uma lista
coordinates = np.concatenate([
    df[['initial_station_latitude', 'initial_station_longitude']].values,
    df[['final_station_latitude', 'final_station_longitude']].values
])

#Calcular a densidade com KDE
kde = gaussian_kde(coordinates.T, bw_method='silverman')  # Usando o método de suavização de Silverman

# Definir a grade de pontos para calcular a densidade
grid_lat = np.linspace(df['initial_station_latitude'].min() - 0.01, df['initial_station_latitude'].max() + 0.01, 100)
grid_lon = np.linspace(df['initial_station_longitude'].min() - 0.01, df['initial_station_longitude'].max() + 0.01, 100)

# Criar a grade de pontos para os quais calcularemos a densidade
grid_points = np.array([(lat, lon) for lat in grid_lat for lon in grid_lon])

# Calcular as densidades nos pontos da grade
densities = kde(grid_points.T)

# Filtrar as hotzones (áreas com alta densidade)
# threshold = 0.005  # Ajuste esse valor conforme necessário
# threshold = np.median(densities)
# mean_density = np.mean(densities)
# std_density = np.std(densities)
# threshold = mean_density + std_density  # Ajuste o multiplicador (1, 2, etc.)
threshold = np.percentile(densities, 75)  # Top 25% densities

hotzones = []


for i, density in enumerate(densities):
    if density > threshold:  # Se a densidade for maior que o limiar
        lat, lon = grid_points[i]
        # Criar um buffer (círculo) ao redor da coordenada de alta densidade
        buffer = Point(lon, lat).buffer(0.002)  # Buffer de 200 metros
        hotzones.append(buffer)
    

# Criar um GeoDataFrame com as hotzones
print(hotzones)
gdf_hotzones = gpd.GeoDataFrame(geometry=hotzones)


with open('hotzones.geojson', 'w') as f:
    f.write(gdf_hotzones.to_json(indent=4, ensure_ascii=False))
    
print("GeoJSON with hotzones saved successfully!")
