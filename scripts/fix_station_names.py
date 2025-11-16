#!/usr/bin/env python3
"""
Script para corrigir nomes de estações problemáticos no banco de dados.

Problemas identificados:
1. Estações com nomes "Placeholder" ou "Place Holder"
2. Nomes com ID duplicado no início
3. Problemas de encoding (à, ã, etc)
4. Nomes duplicados (ex: duas "Estacao Tiradentes")

Uso:
    python3 scripts/fix_station_names.py [--dry-run] [--verbose]

Opções:
    --dry-run   : Simula a execução sem fazer alterações no banco
    --verbose   : Mostra detalhes de cada estação processada
"""

import os
import sys
import django
import argparse
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Station


# Mapeamento de correções conhecidas
CORRECTIONS = {
    # Placeholders USP - IMPORTANTE: Localizar os nomes reais!
    # Coordenadas podem ser usadas no Google Maps para identificar
    245: {
        'old': '245',
        'new': '245 - Raia Olímpica USP',  # Coord: -23.5654, -46.7129 (próximo à raia)
        'reason': 'Placeholder genérico → Nome descritivo baseado em localização'
    },
    247: {
        'old': 'Placeholder 247',
        'new': '247 - Faculdade de Arquitetura',  # Coord: -23.5620, -46.7175
        'reason': 'Placeholder → Nome real da localização'
    },
    248: {
        'old': 'Place Holder 248',
        'new': '248 - Praça do Relógio',  # Coord: -23.5625, -46.7228
        'reason': 'Placeholder → Nome real da localização'
    },
    
    # Correções de formatação e encoding
    249: {
        'old': '249 -BandejÃ£o Central',
        'new': '249 - Bandejão Central',
        'reason': 'Remover ID duplicado + corrigir encoding'
    },
    253: {
        'old': '253 -BIÃNIO POLI USP',
        'new': '253 - Biênio Poli USP',
        'reason': 'Remover ID duplicado + corrigir encoding + normalizar caps'
    },
    259: {
        'old': 'Estacao Tiradentes - 259',
        'new': '259 - Portão 1 USP',  # Diferenciar da 255
        'reason': 'Nome duplicado com ID 255 → Diferenciar localização'
    },
    261: {
        'old': '261- PraÃ§a Pero Vaz de Caminha',
        'new': '261 - Praça Pero Vaz de Caminha',
        'reason': 'Remover ID duplicado + corrigir encoding + espaçamento'
    },
}


def fix_station_names(dry_run=False, verbose=False):
    """
    Corrige nomes problemáticos das estações.
    
    Args:
        dry_run: Se True, não faz alterações no banco (apenas simula)
        verbose: Se True, mostra detalhes de cada estação processada
    """
    print("=" * 80)
    print("🔧 CORREÇÃO DE NOMES DE ESTAÇÕES")
    print("=" * 80)
    
    if dry_run:
        print("⚠️  MODO DRY-RUN: Nenhuma alteração será feita no banco\n")
    
    stats = {
        'fixed': 0,
        'not_found': 0,
        'errors': 0
    }
    
    print(f"📋 Estações a corrigir: {len(CORRECTIONS)}\n")
    
    for station_id, correction in CORRECTIONS.items():
        try:
            station = Station.objects.filter(station_id=station_id).first()
            
            if not station:
                stats['not_found'] += 1
                if verbose:
                    print(f"⚠️  ID {station_id}: Não encontrada no banco")
                continue
            
            old_name = station.name
            new_name = correction['new']
            reason = correction['reason']
            
            # Verificar se já está correto
            if old_name == new_name:
                if verbose:
                    print(f"✓ ID {station_id}: Já corrigido - {new_name}")
                continue
            
            print(f"\n📝 ID {station_id}:")
            print(f"   Antes:  {old_name}")
            print(f"   Depois: {new_name}")
            print(f"   Razão:  {reason}")
            
            if not dry_run:
                station.name = new_name
                station.save()
                stats['fixed'] += 1
                print(f"   ✅ CORRIGIDO!")
            else:
                stats['fixed'] += 1
                print(f"   🔄 (simulação)")
        
        except Exception as e:
            stats['errors'] += 1
            print(f"❌ Erro ao processar estação {station_id}: {e}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DA CORREÇÃO")
    print("=" * 80)
    print(f"✅ Estações corrigidas:    {stats['fixed']}")
    print(f"⚠️  Não encontradas:        {stats['not_found']}")
    print(f"❌ Erros:                   {stats['errors']}")
    
    if dry_run:
        print("\n⚠️  DRY-RUN: Nenhuma alteração foi feita no banco")
        print("   Execute sem --dry-run para aplicar as correções")
    else:
        print("\n✅ Correções aplicadas com sucesso!")
    
    print("=" * 80)
    
    # Aviso sobre nomes placeholder que precisam de investigação manual
    print("\n" + "=" * 80)
    print("⚠️  ATENÇÃO - VERIFICAÇÃO MANUAL NECESSÁRIA")
    print("=" * 80)
    print("""
Os nomes das estações 245, 247 e 248 foram definidos baseado nas coordenadas,
mas DEVEM SER VERIFICADOS MANUALMENTE:

1. ID 245 (-23.5654, -46.7129): Sugerido "Raia Olímpica USP"
   → Verifique no Google Maps se está correto

2. ID 247 (-23.5620, -46.7175): Sugerido "Faculdade de Arquitetura"
   → Verifique no Google Maps se está correto

3. ID 248 (-23.5625, -46.7228): Sugerido "Praça do Relógio"
   → Verifique no Google Maps se está correto

Para verificar:
    https://www.google.com/maps?q=-23.5654,-46.7129
    https://www.google.com/maps?q=-23.5620,-46.7175  
    https://www.google.com/maps?q=-23.5625,-46.7228

Se os nomes estiverem incorretos, edite o dicionário CORRECTIONS
no arquivo scripts/fix_station_names.py e execute novamente.
    """)
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Corrige nomes problemáticos de estações no banco de dados'
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
    
    fix_station_names(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == '__main__':
    main()
