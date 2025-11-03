#!/usr/bin/env python3
"""
Script de teste para o endpoint de fluxos de viagens
Testa diferentes cenários e valida a resposta
"""

import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000/api/trip_flows/"

def test_endpoint(params: Dict = None, description: str = ""):
    """Testa o endpoint com os parâmetros fornecidos"""
    print(f"\n{'='*80}")
    print(f"🧪 Teste: {description}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Número de fluxos retornados: {len(data)}")
            
            if len(data) > 0:
                print(f"\n📈 Top 5 fluxos:")
                for i, flow in enumerate(data[:5], 1):
                    origin = flow['origin_station_name']
                    destination = flow['destination_station_name']
                    count = flow['trip_count']
                    print(f"  {i}. {origin} → {destination}: {count} viagens")
                
                # Validações
                print(f"\n🔍 Validações:")
                
                # Check se não há viagens origem = destino
                same_station = [f for f in data if f['origin_station_id'] == f['destination_station_id']]
                if same_station:
                    print(f"  ⚠️  Encontradas {len(same_station)} viagens onde origem = destino")
                else:
                    print(f"  ✅ Nenhuma viagem com origem = destino")
                
                # Check coordenadas válidas
                invalid_coords = [f for f in data if 
                    not all([f['origin_coords'], f['destination_coords']]) or
                    len(f['origin_coords']) != 2 or 
                    len(f['destination_coords']) != 2]
                if invalid_coords:
                    print(f"  ⚠️  Encontrados {len(invalid_coords)} fluxos com coordenadas inválidas")
                else:
                    print(f"  ✅ Todas as coordenadas são válidas")
                
                # Check trip_count mínimo
                min_count = min(f['trip_count'] for f in data)
                max_count = max(f['trip_count'] for f in data)
                print(f"  📊 Range de viagens: {min_count} - {max_count}")
                
            else:
                print("⚠️  Nenhum fluxo retornado")
                
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")

def main():
    print("🚀 Iniciando testes do endpoint de Trip Flows")
    print(f"Endpoint: {BASE_URL}")
    
    # Teste 1: Padrão (weekdays, top 20)
    test_endpoint(
        params={'limit': 20, 'min_trips': 50},
        description="Padrão - Top 20 fluxos com mínimo 50 viagens"
    )
    
    # Teste 2: Filtro USP
    test_endpoint(
        params={'usp': 'true', 'limit': 15, 'min_trips': 20},
        description="Filtro USP - Estações 242-260"
    )
    
    # Teste 3: Final de semana
    test_endpoint(
        params={'days': '5,6', 'limit': 15, 'min_trips': 20},
        description="Final de semana (sábado e domingo)"
    )
    
    # Teste 4: Apenas segunda e sexta
    test_endpoint(
        params={'days': '0,4', 'limit': 15, 'min_trips': 30},
        description="Segunda e sexta-feira"
    )
    
    # Teste 5: Excluir meses de férias
    test_endpoint(
        params={'months': '1,2,7,12', 'limit': 15, 'min_trips': 40},
        description="Excluindo meses de férias (Jan, Fev, Jul, Dez)"
    )
    
    # Teste 6: Limite alto
    test_endpoint(
        params={'limit': 100, 'min_trips': 10},
        description="Top 100 fluxos com mínimo 10 viagens"
    )
    
    # Teste 7: USP + Weekdays
    test_endpoint(
        params={'usp': 'true', 'days': '0,1,2,3,4', 'limit': 20},
        description="USP + Dias úteis"
    )
    
    print(f"\n{'='*80}")
    print("✅ Testes concluídos!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
