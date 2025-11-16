#!/usr/bin/env python3
"""
ANÁLISE 3: INTEGRAÇÃO MODAL - METRÔ/CPTM COMO HUBS
===================================================

Objetivo: Analisar viagens que conectam transporte público ao campus,
caracterizando o conceito de "primeira/última milha".

Contexto USP:
- Estação Metrô Butantã é a principal porta de entrada
- Portões P1, P2, P3 também são importantes
- Estação Cidade Universitária (CPTM) conecta ao trem
- Padrão assimétrico: manhã (entrada) vs tarde (saída)

Consultas SQL documentadas para verificação do professor.
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db.models import Count, Q, F
from ciclovias.models import Trip, Station

# Diretório de saída
OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def print_sql_query(description, queryset):
    """Imprime a query SQL para documentação"""
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")
    print(queryset.query)
    print(f"{'='*80}\n")

# Estações de entrada/saída do campus (transporte público)
ESTACOES_TRANSPORTE = [
    'Metrô Butantã',
    'Cidade Universitária (CPTM)',
    'Portão 1',
    'Portão 2', 
    'Portão 3'
]

def analise_integracao_modal():
    """
    Análise principal: Integração com transporte público
    """
    
    print("="*80)
    print("ANÁLISE 3: INTEGRAÇÃO MODAL - PRIMEIRA/ÚLTIMA MILHA")
    print("="*80)
    
    # =================================================================
    # CONSULTA 1: Viagens que COMEÇAM em estações de transporte
    # =================================================================
    viagens_entrada = Trip.objects.filter(
        initial_station_name__in=ESTACOES_TRANSPORTE
    ).values('initial_station_name').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print_sql_query(
        "Viagens que COMEÇAM em estações de transporte público",
        viagens_entrada
    )
    
    # =================================================================
    # CONSULTA 2: Viagens que TERMINAM em estações de transporte
    # =================================================================
    viagens_saida = Trip.objects.filter(
        final_station_name__in=ESTACOES_TRANSPORTE
    ).values('final_station_name').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print_sql_query(
        "Viagens que TERMINAM em estações de transporte público",
        viagens_saida
    )
    
    # =================================================================
    # CONSULTA 3: Viagens que TOCAM transporte (entrada OU saída)
    # =================================================================
    viagens_transporte = Trip.objects.filter(
        Q(initial_station_name__in=ESTACOES_TRANSPORTE) |
        Q(final_station_name__in=ESTACOES_TRANSPORTE)
    ).count()
    
    total_viagens = Trip.objects.count()
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de viagens no sistema: {total_viagens:,}")
    print(f"   Viagens conectadas a transporte público: {viagens_transporte:,}")
    print(f"   Percentual de integração modal: {viagens_transporte/total_viagens*100:.1f}%")
    
    # Conversões para DataFrames
    df_entrada = pd.DataFrame(list(viagens_entrada))
    df_saida = pd.DataFrame(list(viagens_saida))
    
    # =================================================================
    # ANÁLISE POR ESTAÇÃO
    # =================================================================
    print(f"\n🚇 VIAGENS POR ESTAÇÃO DE TRANSPORTE:")
    print(f"\n{'Estação':<35} {'Entradas':>12} {'Saídas':>12} {'Total':>12}")
    print("-" * 75)
    
    estatisticas_estacoes = []
    for estacao in ESTACOES_TRANSPORTE:
        entradas = df_entrada[df_entrada['initial_station_name'] == estacao]['total'].sum() if not df_entrada.empty else 0
        saidas = df_saida[df_saida['final_station_name'] == estacao]['total'].sum() if not df_saida.empty else 0
        total = entradas + saidas
        
        print(f"{estacao:<35} {int(entradas):>12,} {int(saidas):>12,} {int(total):>12,}")
        
        estatisticas_estacoes.append({
            'estacao': estacao,
            'entradas': int(entradas),
            'saidas': int(saidas),
            'total': int(total),
            'saldo': int(entradas - saidas)
        })
    
    df_estatisticas = pd.DataFrame(estatisticas_estacoes)
    
    # =================================================================
    # CONSULTA 4: Principais DESTINOS desde o Metrô Butantã (manhã)
    # =================================================================
    print(f"\n🎯 PRINCIPAIS DESTINOS DESDE METRÔ BUTANTÃ (período da manhã 6h-12h):")
    
    destinos_metro = Trip.objects.filter(
        initial_station_name='Metrô Butantã',
        start_hour__gte=6,
        start_hour__lt=12
    ).values('final_station_name').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    print_sql_query(
        "Top 10 destinos desde Metrô Butantã pela manhã",
        destinos_metro
    )
    
    for idx, dest in enumerate(destinos_metro, 1):
        print(f"   {idx:2d}. {dest['final_station_name']:<40} {dest['total']:>6,} viagens")
    
    # =================================================================
    # CONSULTA 5: Principais ORIGENS para o Metrô Butantã (tarde)
    # =================================================================
    print(f"\n🏁 PRINCIPAIS ORIGENS PARA METRÔ BUTANTÃ (período da tarde 16h-20h):")
    
    origens_metro = Trip.objects.filter(
        final_station_name='Metrô Butantã',
        start_hour__gte=16,
        start_hour__lt=20
    ).values('initial_station_name').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    print_sql_query(
        "Top 10 origens para Metrô Butantã à tarde",
        origens_metro
    )
    
    for idx, orig in enumerate(origens_metro, 1):
        print(f"   {idx:2d}. {orig['initial_station_name']:<40} {orig['total']:>6,} viagens")
    
    # =================================================================
    # CONSULTA 6: Padrão por hora - Metrô Butantã (entrada vs saída)
    # =================================================================
    print(f"\n⏰ Analisando padrão horário do Metrô Butantã...")
    
    # Saindo do Metrô (entrada no campus)
    saindo_metro = Trip.objects.filter(
        initial_station_name='Metrô Butantã'
    ).values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    # Indo para o Metrô (saída do campus)
    indo_metro = Trip.objects.filter(
        final_station_name='Metrô Butantã'
    ).values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    print_sql_query(
        "Viagens SAINDO do Metrô por hora",
        saindo_metro
    )
    
    print_sql_query(
        "Viagens INDO PARA o Metrô por hora",
        indo_metro
    )
    
    # Preparar dados para gráfico
    horas = np.arange(0, 24)
    saindo_array = np.zeros(24)
    indo_array = np.zeros(24)
    
    for item in saindo_metro:
        if item['start_hour'] is not None:
            saindo_array[item['start_hour']] = item['total']
    
    for item in indo_metro:
        if item['start_hour'] is not None:
            indo_array[item['start_hour']] = item['total']
    
    # =================================================================
    # GRÁFICO 1: Entrada vs Saída por estação
    # =================================================================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(ESTACOES_TRANSPORTE))
    width = 0.35
    
    ax.bar(x - width/2, df_estatisticas['entradas'], width,
           label='Viagens de Entrada (saindo da estação)', color='#06A77D', alpha=0.8, edgecolor='black')
    ax.bar(x + width/2, df_estatisticas['saidas'], width,
           label='Viagens de Saída (chegando na estação)', color='#E63946', alpha=0.8, edgecolor='black')
    
    ax.set_title('Integração Modal: Viagens por Estação de Transporte Público', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Estação', fontsize=12)
    ax.set_ylabel('Número de Viagens', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([e.replace(' ', '\n') for e in ESTACOES_TRANSPORTE], fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath1 = os.path.join(OUTPUT_DIR, 'analise_08_integracao_modal_estacoes.png')
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath1}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 2: Padrão horário Metrô Butantã (assimetria manhã/tarde)
    # =================================================================
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = np.arange(24)
    width = 0.35
    
    ax.bar(x - width/2, saindo_array, width,
           label='Saindo do Metrô (entrada no campus)', color='#2E86AB', alpha=0.8, edgecolor='black')
    ax.bar(x + width/2, indo_array, width,
           label='Indo para o Metrô (saída do campus)', color='#F18F01', alpha=0.8, edgecolor='black')
    
    # Marcar horários típicos
    ax.axvspan(6, 10, alpha=0.1, color='green', label='Pico manhã (entrada)')
    ax.axvspan(16, 20, alpha=0.1, color='red', label='Pico tarde (saída)')
    
    ax.set_title('Metrô Butantã: Padrão "Maré" - Entrada pela Manhã, Saída à Tarde', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Hora do Dia', fontsize=12)
    ax.set_ylabel('Número de Viagens', fontsize=12)
    ax.set_xticks(horas)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath2 = os.path.join(OUTPUT_DIR, 'analise_08_integracao_modal_horario_metro.png')
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath2}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 3: Saldo (entradas - saídas) por estação
    # =================================================================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    cores = ['#06A77D' if s > 0 else '#E63946' for s in df_estatisticas['saldo']]
    
    bars = ax.bar(df_estatisticas['estacao'], df_estatisticas['saldo'], 
                  color=cores, alpha=0.8, edgecolor='black')
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_title('Saldo de Viagens (Entradas - Saídas) por Estação\n' + 
                 'Positivo = Mais entradas | Negativo = Mais saídas', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Estação', fontsize=12)
    ax.set_ylabel('Saldo (Entradas - Saídas)', fontsize=12)
    ax.set_xticklabels([e.replace(' ', '\n') for e in df_estatisticas['estacao']], fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath3 = os.path.join(OUTPUT_DIR, 'analise_08_integracao_modal_saldo.png')
    plt.savefig(filepath3, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath3}")
    plt.close()
    
    # =================================================================
    # SALVAR DADOS TABULARES
    # =================================================================
    csv_path1 = os.path.join(OUTPUT_DIR, 'analise_08_integracao_modal_estacoes.csv')
    df_estatisticas.to_csv(csv_path1, index=False)
    
    csv_path2 = os.path.join(OUTPUT_DIR, 'analise_08_integracao_modal_horario.csv')
    df_horario = pd.DataFrame({
        'hora': horas,
        'saindo_metro': saindo_array.astype(int),
        'indo_metro': indo_array.astype(int)
    })
    df_horario.to_csv(csv_path2, index=False)
    
    print(f"\n✅ Dados salvos:")
    print(f"   {csv_path1}")
    print(f"   {csv_path2}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE 3 CONCLUÍDA!")
    print("="*80)
    
    return {
        'total_viagens': total_viagens,
        'viagens_transporte': viagens_transporte,
        'percentual_integracao': viagens_transporte/total_viagens*100 if total_viagens > 0 else 0
    }

if __name__ == '__main__':
    resultado = analise_integracao_modal()
    print(f"\n📊 Resumo: {resultado['percentual_integracao']:.1f}% das viagens envolvem transporte público")
