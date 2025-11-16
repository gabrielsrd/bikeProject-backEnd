#!/usr/bin/env python3
"""
Script para corrigir coordenadas faltantes nas estações do banco de dados.

Este script resolve o problema de estações cadastradas sem latitude/longitude,
usando as coordenadas médias das viagens já importadas no banco SQLite.

Estratégia:
-----------
Para cada estação sem coordenadas, o script:
1. Busca viagens onde a estação aparece como origem ou destino
2. Calcula a média das coordenadas dessas viagens (dados reais de uso)
3. Atualiza a estação com as coordenadas médias

Vantagens desta abordagem:
- Usa dados REAIS já importados no banco
- Não depende de arquivos GeoJSON externos (que podem estar desatualizados)
- Coordenadas refletem o uso real das estações

Uso:
    python3 scripts/fix_missing_coordinates.py [--dry-run] [--verbose]

Opções:
    --dry-run   : Simula a execução sem fazer alterações no banco
    --verbose   : Mostra detalhes de cada estação processada
"""

import os
import sys
import django
import json
import argparse
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Avg, Count, Q


def get_coordinates_from_trips(station_id):
    """
    Obtém coordenadas de uma estação a partir das viagens no banco.
    Usa a média das coordenadas quando a estação aparece em múltiplas viagens.
    """
    # Buscar viagens onde esta estação é origem
    initial_trips = Trip.objects.filter(
        initial_station__station_id=station_id,
        initial_station_latitude__isnull=False,
        initial_station_longitude__isnull=False
    ).aggregate(
        avg_lat=Avg('initial_station_latitude'),
        avg_lon=Avg('initial_station_longitude'),
        count=Count('id')
    )
    
    # Buscar viagens onde esta estação é destino
    final_trips = Trip.objects.filter(
        final_station__station_id=station_id,
        final_station_latitude__isnull=False,
        final_station_longitude__isnull=False
    ).aggregate(
        avg_lat=Avg('final_station_latitude'),
        avg_lon=Avg('final_station_longitude'),
        count=Count('id')
    )
    
    # Priorizar coordenadas de viagens iniciais (mais confiáveis)
    if initial_trips['count'] and initial_trips['avg_lat']:
        return {
            'latitude': initial_trips['avg_lat'],
            'longitude': initial_trips['avg_lon'],
            'source': f'trips_initial (n={initial_trips["count"]})'
        }
    elif final_trips['count'] and final_trips['avg_lat']:
        return {
            'latitude': final_trips['avg_lat'],
            'longitude': final_trips['avg_lon'],
            'source': f'trips_final (n={final_trips["count"]})'
        }
    
    return None


def fix_missing_coordinates(dry_run=False, verbose=False):
    """
    Corrige coordenadas faltantes nas estações usando dados do banco SQLite.
    
    Args:
        dry_run: Se True, não faz alterações no banco (apenas simula)
        verbose: Se True, mostra detalhes de cada estação processada
    """
    print("=" * 80)
    print("🔧 CORREÇÃO DE COORDENADAS FALTANTES")
    print("=" * 80)
    
    if dry_run:
        print("⚠️  MODO DRY-RUN: Nenhuma alteração será feita no banco\n")
    
    # Buscar estações sem coordenadas
    stations_without_coords = Station.objects.filter(
        Q(latitude__isnull=True) | Q(longitude__isnull=True)
    )
    
    total_missing = stations_without_coords.count()
    print(f"📊 Estações sem coordenadas: {total_missing}")
    print(f"📊 Estações totais no banco: {Station.objects.count()}\n")
    
    if total_missing == 0:
        print("✅ Todas as estações já possuem coordenadas!")
        return
    
    # Processar cada estação
    stats = {
        'fixed_trips': 0,
        'still_missing': 0,
        'errors': 0
    }
    
    print("🔄 Processando estações...\n")
    print("📍 Buscando coordenadas nas viagens do banco SQLite...")
    print()
    
    for station in stations_without_coords:
        try:
            coords = None
            
            # Buscar coordenadas nas viagens do banco
            if station.station_id:
                coords = get_coordinates_from_trips(station.station_id)
                if coords:
                    stats['fixed_trips'] += 1
            
            # Aplicar correção
            if coords:
                if verbose or stats['fixed_trips'] <= 10:
                    print(f"✓ Estação {station.station_id} - {station.name[:40]}")
                    print(f"  → Lat: {coords['latitude']:.6f}, Lon: {coords['longitude']:.6f}")
                    print(f"  → Fonte: {coords['source']}")
                
                if not dry_run:
                    station.latitude = coords['latitude']
                    station.longitude = coords['longitude']
                    station.save()
            else:
                stats['still_missing'] += 1
                if verbose:
                    print(f"⚠️  Estação {station.station_id} - {station.name[:40]}")
                    print(f"  → Sem viagens no banco (período não importado)")
        
        except Exception as e:
            stats['errors'] += 1
            if verbose:
                print(f"❌ Erro ao processar estação {station.station_id}: {e}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DA CORREÇÃO")
    print("=" * 80)
    print(f"✅ Corrigidas via viagens SQLite: {stats['fixed_trips']}")
    print(f"⚠️  Ainda sem coordenadas:         {stats['still_missing']}")
    print(f"❌ Erros durante processamento:   {stats['errors']}")
    print(f"\n🎯 Total de correções: {stats['fixed_trips']}/{total_missing}")
    
    if stats['still_missing'] > 0:
        print(f"\n⚠️  ATENÇÃO: {stats['still_missing']} estações ainda sem coordenadas")
        print("   Estas estações não têm viagens importadas no período atual (2018-2022).")
        print("   São provavelmente estações criadas após 2022 ou que nunca foram usadas.")
    
    if dry_run:
        print("\n⚠️  DRY-RUN: Nenhuma alteração foi feita no banco")
        print("   Execute sem --dry-run para aplicar as correções")
    else:
        print("\n✅ Correções aplicadas com sucesso!")
    
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Corrige coordenadas faltantes nas estações do banco de dados'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula a execução sem fazer alterações no banco'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostra detalhes de cada estação processada'
    )
    
    args = parser.parse_args()
    
    fix_missing_coordinates(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == '__main__':
    main()
