#!/usr/bin/env python3
"""
Script 01: Verificação e Estatísticas Básicas dos Dados
========================================================

Este script examina o banco de dados e gera estatísticas básicas sobre:
- Total de viagens e estações
- Viagens USP (estações 242-260)
- Período temporal dos dados
- Distribuição por estação

Autor: Gabriel da Silva Alves
Data: Novembro 2025
Projeto: TCC - Análise de viagens de bicicletas compartilhadas na USP
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from ciclovias.models import Station, Trip

def print_section(title):
    """Imprime um cabeçalho de seção formatado"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def verificar_estrutura_basica():
    """Verifica a estrutura básica do banco de dados"""
    print_section("ESTRUTURA BÁSICA DO BANCO DE DADOS")
    
    # Contar estações e viagens
    total_estacoes = Station.objects.count()
    total_viagens = Trip.objects.count()
    
    print(f"\n📊 Total de estações cadastradas: {total_estacoes:,}")
    print(f"📊 Total de viagens registradas: {total_viagens:,}")
    
    return total_estacoes, total_viagens

def analisar_periodo_temporal():
    """Analisa o período temporal dos dados"""
    print_section("PERÍODO TEMPORAL DOS DADOS")
    
    # Buscar primeira e última viagem
    primeira_viagem = Trip.objects.order_by('start_time').first()
    ultima_viagem = Trip.objects.order_by('-start_time').first()
    
    if primeira_viagem and ultima_viagem:
        print(f"\n📅 Primeira viagem: {primeira_viagem.start_time.strftime('%d/%m/%Y %H:%M')}")
        print(f"📅 Última viagem: {ultima_viagem.start_time.strftime('%d/%m/%Y %H:%M')}")
        
        # Calcular duração do dataset
        duracao = ultima_viagem.start_time - primeira_viagem.start_time
        anos = duracao.days / 365.25
        print(f"📅 Período total: {duracao.days:,} dias ({anos:.1f} anos)")
        
        return primeira_viagem.start_time, ultima_viagem.start_time
    
    return None, None

def identificar_estacoes_usp():
    """Identifica e analisa estações do campus USP"""
    print_section("ESTAÇÕES DO CAMPUS USP (17 estações)")
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    total_estacoes_usp = estacoes_usp.count()
    print(f"\n📍 Total de estações USP: {total_estacoes_usp}")
    
    if total_estacoes_usp > 0:
        print("\n📋 Lista de estações USP:")
        print("-" * 80)
        for estacao in estacoes_usp:
            # Contar viagens que começam nesta estação
            viagens_saida = Trip.objects.filter(initial_station=estacao).count()
            # Contar viagens que terminam nesta estação
            viagens_chegada = Trip.objects.filter(final_station=estacao).count()
            total_viagens = viagens_saida + viagens_chegada
            
            print(f"  {estacao.station_id:3d} - {estacao.name:40s} | "
                  f"Saídas: {viagens_saida:6,} | Chegadas: {viagens_chegada:6,} | "
                  f"Total: {total_viagens:7,}")
    
    return estacoes_usp

def analisar_viagens_usp():
    """Analisa viagens que envolvem o campus USP"""
    print_section("ANÁLISE DE VIAGENS USP")
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks)
    
    # Viagens que começam OU terminam na USP
    viagens_usp = Trip.objects.filter(
        initial_station__in=estacoes_usp
    ) | Trip.objects.filter(
        final_station__in=estacoes_usp
    )
    
    total_viagens_usp = viagens_usp.count()
    total_viagens = Trip.objects.count()
    percentual = (total_viagens_usp / total_viagens * 100) if total_viagens > 0 else 0
    
    print(f"\n🚴 Viagens que envolvem o campus USP: {total_viagens_usp:,}")
    print(f"🚴 Percentual do total: {percentual:.2f}%")
    
    # Viagens apenas dentro do campus (ambas estações na USP)
    viagens_internas = Trip.objects.filter(
        initial_station__in=estacoes_usp,
        final_station__in=estacoes_usp
    ).count()
    
    print(f"🚴 Viagens internas (USP → USP): {viagens_internas:,}")
    print(f"🚴 Viagens externas (USP ↔ Fora): {total_viagens_usp - viagens_internas:,}")
    
    return total_viagens_usp, viagens_internas

def analisar_top_estacoes():
    """Identifica as estações mais utilizadas"""
    print_section("TOP 10 ESTAÇÕES MAIS UTILIZADAS (GERAL)")
    
    # Criar dicionário para contar viagens por estação
    estacoes_dict = {}
    
    for estacao in Station.objects.all():
        viagens_saida = Trip.objects.filter(initial_station=estacao).count()
        viagens_chegada = Trip.objects.filter(final_station=estacao).count()
        total = viagens_saida + viagens_chegada
        
        if total > 0:
            estacoes_dict[estacao.station_id] = {
                'nome': estacao.name,
                'saidas': viagens_saida,
                'chegadas': viagens_chegada,
                'total': total
            }
    
    # Ordenar por total
    top_estacoes = sorted(estacoes_dict.items(), 
                         key=lambda x: x[1]['total'], 
                         reverse=True)[:10]
    
    print("\n" + "-" * 90)
    print(f"{'Pos':3s} | {'ID':3s} | {'Nome':40s} | {'Saídas':8s} | {'Chegadas':8s} | {'Total':10s}")
    print("-" * 90)
    
    for i, (station_id, dados) in enumerate(top_estacoes, 1):
        print(f"{i:3d} | {station_id:3d} | {dados['nome']:40s} | "
              f"{dados['saidas']:8,} | {dados['chegadas']:8,} | "
              f"{dados['total']:10,}")
    
    return top_estacoes

def gerar_resumo_executivo():
    """Gera um resumo executivo dos dados"""
    print_section("RESUMO EXECUTIVO")
    
    total_viagens = Trip.objects.count()
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks)
    
    viagens_usp = Trip.objects.filter(
        initial_station__in=estacoes_usp
    ) | Trip.objects.filter(
        final_station__in=estacoes_usp
    )
    
    viagens_internas = Trip.objects.filter(
        initial_station__in=estacoes_usp,
        final_station__in=estacoes_usp
    ).count()
    
    primeira = Trip.objects.order_by('start_time').first()
    ultima = Trip.objects.order_by('-start_time').first()
    
    print("\n📊 DADOS GERAIS:")
    print(f"   • Total de viagens no banco: {total_viagens:,}")
    print(f"   • Período: {primeira.start_time.strftime('%d/%m/%Y')} a {ultima.start_time.strftime('%d/%m/%Y')}")
    print(f"   • Total de estações: {Station.objects.count()}")
    
    print("\n🎓 DADOS USP:")
    print(f"   • Estações no campus: {estacoes_usp.count()}")
    print(f"   • Viagens USP (origem OU destino): {viagens_usp.count():,} ({viagens_usp.count()/total_viagens*100:.2f}%)")
    print(f"   • Viagens internas (USP → USP): {viagens_internas:,} ({viagens_internas/viagens_usp.count()*100:.2f}% das viagens USP)")
    print(f"   • Viagens externas (USP ↔ Fora): {viagens_usp.count() - viagens_internas:,}")

def salvar_estatisticas_csv():
    """Salva estatísticas em CSV para análises posteriores"""
    print_section("SALVANDO ESTATÍSTICAS EM CSV")
    
    # Criar diretório de saída se não existir
    output_dir = 'analises_monografia/resultados'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Estatísticas por estação USP
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    dados_estacoes = []
    for estacao in estacoes_usp:
        viagens_saida = Trip.objects.filter(initial_station=estacao).count()
        viagens_chegada = Trip.objects.filter(final_station=estacao).count()
        
        dados_estacoes.append({
            'station_id': estacao.station_id,
            'nome': estacao.name,
            'latitude': estacao.latitude,
            'longitude': estacao.longitude,
            'viagens_saida': viagens_saida,
            'viagens_chegada': viagens_chegada,
            'total_viagens': viagens_saida + viagens_chegada
        })
    
    df_estacoes = pd.DataFrame(dados_estacoes)
    csv_path = f'{output_dir}/estacoes_usp_estatisticas.csv'
    df_estacoes.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\n✅ Estatísticas de estações salvas em: {csv_path}")
    
    # 2. Resumo geral
    resumo = {
        'total_viagens': [Trip.objects.count()],
        'total_estacoes': [Station.objects.count()],
        'estacoes_usp': [estacoes_usp.count()],
        'viagens_usp': [(Trip.objects.filter(initial_station__in=estacoes_usp) | 
                        Trip.objects.filter(final_station__in=estacoes_usp)).count()],
        'data_inicio': [Trip.objects.order_by('start_time').first().start_time.strftime('%Y-%m-%d')],
        'data_fim': [Trip.objects.order_by('-start_time').first().start_time.strftime('%Y-%m-%d')]
    }
    
    df_resumo = pd.DataFrame(resumo)
    csv_resumo = f'{output_dir}/resumo_geral.csv'
    df_resumo.to_csv(csv_resumo, index=False, encoding='utf-8')
    print(f"✅ Resumo geral salvo em: {csv_resumo}")
    
    print(f"\n📁 Arquivos salvos no diretório: {output_dir}/")

def main():
    """Função principal"""
    print("\n" + "🚴" * 40)
    print(" " * 20 + "ANÁLISE DE DADOS - BIKESCIENCE USP")
    print(" " * 20 + "Script 01: Verificação de Dados")
    print("🚴" * 40)
    
    try:
        # Executar análises
        verificar_estrutura_basica()
        analisar_periodo_temporal()
        identificar_estacoes_usp()
        analisar_viagens_usp()
        analisar_top_estacoes()
        gerar_resumo_executivo()
        salvar_estatisticas_csv()
        
        print("\n" + "=" * 80)
        print("  ✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
