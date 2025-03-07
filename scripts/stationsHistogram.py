import pandas as pd
import re

def extract_station_id(name):
    match = re.match(r'(\d+)', name)
    if match:
        return int(match.group(1))
    else:
        return None  # Caso não haja número no nome

# Carregar o arquivo CSV
csv_file = "../dataRaw/userTrips.csv"
df = pd.read_csv(csv_file)

df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])

df['start_day'] = df['start_time'].dt.dayofweek  # 0=segunda, 1=terça, ..., 6=domingo
df['end_day'] = df['end_time'].dt.dayofweek
df['start_hour'] = df['start_time'].dt.hour
df['end_hour'] = df['end_time'].dt.hour

# Filtrar para dias úteis (dayofweek < 5)
df_departures = df[df['start_day'] < 5]
df_arrivals = df[df['end_day'] < 5]

# Calcular contagens de partidas por estação dia e hora
departures_counts = df_departures.groupby(['initial_station_name', 'start_day', 'start_hour']).size().reset_index(name='departures')

# Calcular contagens de chegadas por estaçã dia e hora
arrivals_counts = df_arrivals.groupby(['final_station_name', 'end_day', 'end_hour']).size().reset_index(name='arrivals')

# Extrair o ID da estação para partidas e chegadas
departures_counts['station_id'] = departures_counts['initial_station_name'].apply(extract_station_id)
arrivals_counts['station_id'] = arrivals_counts['final_station_name'].apply(extract_station_id)

departures_counts = departures_counts.rename(columns={
    'initial_station_name': 'station',
    'start_day': 'day',
    'start_hour': 'hour'
})

arrivals_counts = arrivals_counts.rename(columns={
    'final_station_name': 'station',
    'end_day': 'day',
    'end_hour': 'hour'
})

histogram_data = pd.merge(departures_counts, arrivals_counts, on=['station_id', 'day', 'hour'], how='outer').fillna(0)

histogram_data['station'] = histogram_data['station_x'].combine_first(histogram_data['station_y'])

histogram_data = histogram_data[['station_id', 'station', 'day', 'hour', 'departures', 'arrivals']]

#  JSON
histogram_data.to_json('station_histogram_with_id.json', orient='records', indent=4)

print("Arquivo JSON 'station_histogram_with_id.json' gerado com sucesso!")