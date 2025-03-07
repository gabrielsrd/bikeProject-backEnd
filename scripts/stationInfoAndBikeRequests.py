import pandas as pd
import geopandas as gpd

# Carregar o arquivo CSV
csv_file = "../dataRaw/userTrips.csv"
df = pd.read_csv(csv_file)

# Calcular os horários de maior solicitação de bikes
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['start_hour'] = df['start_time'].dt.hour
df['end_hour'] = df['end_time'].dt.hour

# Calcular o número de partidas por estação e hora
hourly_departures = df.groupby(['initial_station_name', 'start_hour']).size().reset_index(name='departures')

# Calcular o número de chegadas por estação e hora
hourly_arrivals = df.groupby(['final_station_name', 'end_hour']).size().reset_index(name='arrivals')

# Mesclar as contagens de partidas e chegadas
hourly_counts = pd.merge(hourly_departures, hourly_arrivals, left_on=['initial_station_name', 'start_hour'], right_on=['final_station_name', 'end_hour'], how='outer').fillna(0)
hourly_counts = hourly_counts.rename(columns={'initial_station_name': 'station', 'start_hour': 'hour'}).drop(columns=['final_station_name', 'end_hour'])

# Calcular o número de entradas e saídas por estação
station_departures = df.groupby('initial_station_name').size().reset_index(name='departures')
station_arrivals = df.groupby('final_station_name').size().reset_index(name='arrivals')
station_counts = pd.merge(station_departures, station_arrivals, left_on='initial_station_name', right_on='final_station_name', how='outer').fillna(0)
station_counts['total'] = station_counts['departures'] + station_counts['arrivals']
station_counts = station_counts.rename(columns={'initial_station_name': 'station'}).drop(columns=['final_station_name'])

# Salvar os horários de maior solicitação em um arquivo JSON
hourly_counts.to_json('hourly_counts.json', orient='records', indent=4)

# Salvar o número de entradas e saídas por estação em um arquivo JSON
station_counts.to_json('station_counts.json', orient='records', indent=4)

print("JSON with hourly counts saved successfully!")
print("JSON with station counts saved successfully!")
