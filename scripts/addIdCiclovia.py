import json

def adicionar_id_ciclovias(geojson_file, output_file):
    """Adiciona IDs sequenciais às features de ciclovias.

    Esta função lê um arquivo GeoJSON contendo dados de ciclovias, adiciona um ID único a cada feature 
    e salva o GeoJSON modificado em um novo arquivo.  A adição de IDs é crucial para o meu TCC, pois 
    permite referenciar e analisar as ciclovias individualmente em outras partes da minha pesquisa.

    Args:
        geojson_file: Caminho para o arquivo GeoJSON de entrada (ex: "ciclovias.geojson").
        output_file: Caminho para o arquivo GeoJSON de saída (ex: "ciclovias_com_id.geojson").
    """

    try:
        # Abrir o arquivo GeoJSON em modo de leitura ('r') com codificação UTF-8 para suportar caracteres especiais.
        with open(geojson_file, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{geojson_file}' não encontrado. Verifique o caminho.")
        return  
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{geojson_file}' não é um GeoJSON válido. Verifique o formato.")
        return 


    # Inicializar um contador para gerar IDs sequenciais para as ciclovias.
    id_counter = 1

    # Iterar sobre cada feature (ciclovia) na lista 'features' do GeoJSON.
    for feature in geojson_data['features']:
        # O valor do ID é o valor atual do contador.
        feature['properties']['id'] = id_counter

        id_counter += 1

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2)
        print(f"GeoJSON com IDs adicionados salvo em '{output_file}'.")

    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")



input_file = "../dataClean/ciclovia.geojson" 
output_file = "../dataClean/ciclovia.geojson"
adicionar_id_ciclovias(input_file, output_file)