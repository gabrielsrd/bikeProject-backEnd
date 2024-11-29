import json
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_geojson(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# Função para calcular a menor distância e cicloEstação mais próxima
def calculate_nearest_station(ciclovias, ciclo_stations):
    # Transformar cicloEstações em objetos Shapely Point
    stations = [
        {"id": feature["properties"]["id"], "geometry": Point(feature["geometry"]["coordinates"])}
        for feature in ciclo_stations["features"]
    ]
    
    # Iterar sobre as ciclovias para encontrar a mais próxima
    for feature in ciclovias["features"]:
        try:
            line = LineString(feature["geometry"]["coordinates"])  
        except:
            continue
        # Encontrar a estação mais próxima
        min_distance = float("inf")
        closest_station_id = None
        
        for station in stations:
            distance = line.distance(station["geometry"])  # Distância ponto-reta
            if distance < min_distance:
                min_distance = distance
                closest_station_id = station["id"]
        
        # Adicionar informações na propriedade da ciclovia
        feature["properties"]["closest_station_id"] = closest_station_id
        feature["properties"]["distance_to_closest_station_m"] = round(min_distance * 111320, 2)  # Convertendo para metros
    
    return ciclovias

ciclovias_path = "../dataClean/ciclovias_com_id.geojson"
ciclo_stations_path = "../dataClean/estacoes.geojson"
output_path = "../dataClean/ciclovias_com_distancia.geojson"

# Carregar os arquivos GeoJSON
ciclovias_data = load_geojson(ciclovias_path)
ciclo_stations_data = load_geojson(ciclo_stations_path)

updated_ciclovias = calculate_nearest_station(ciclovias_data, ciclo_stations_data)

# Salvar o GeoJSON atualizado
save_geojson(updated_ciclovias, output_path)

print(f"Arquivo salvo em: {output_path}")
