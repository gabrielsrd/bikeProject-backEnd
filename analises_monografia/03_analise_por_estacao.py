#!/usr/bin/env python3
"""
Script 03: Análise por Estação
================================

Este script analisa cada estação USP individualmente:
- Ranking de estações por volume
- Padrão de uso por hora para cada estação
- Comparação entre estações
- Identificação de estações com padrões similares

Gera gráficos comparativos para a monografia.

Autor: Gabriel da Silva Alves
Data: Novembro 2025
Projeto: TCC - Análise de viagens de bicicletas compartilhadas na USP
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Q

# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Criar diretório de saída
OUTPUT_DIR = 'analises_monografia/resultados/graficos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ranking_estacoes():
    """Gera ranking de estações por volume de viagens"""
    print("\n" + "="*80)
    print("  RANKING DE ESTAÇÕES USP")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    dados_estacoes = []
    for estacao in estacoes_usp:
        viagens_saida = Trip.objects.filter(initial_station=estacao).count()
        viagens_chegada = Trip.objects.filter(final_station=estacao).count()
        total = viagens_saida + viagens_chegada
        
        dados_estacoes.append({
            'station_id': estacao.station_id,
            'nome': estacao.name,
            'saidas': viagens_saida,
            'chegadas': viagens_chegada,
            'total': total,
            'balanco': viagens_saida - viagens_chegada
        })
    
    df = pd.DataFrame(dados_estacoes).sort_values('total', ascending=False)
    
    # Estatísticas
    print(f"\n📊 Total de estações USP: {len(df)}")
    print(f"📊 Total de viagens (soma): {df['total'].sum():,}")
    print(f"\n🏆 TOP 5 ESTAÇÕES:")
    for i, row in df.head(5).iterrows():
        print(f"   {row['station_id']:3d} - {row['nome']:40s}: {row['total']:7,} viagens")
    
    print(f"\n📉 BOTTOM 5 ESTAÇÕES:")
    for i, row in df.tail(5).iterrows():
        print(f"   {row['station_id']:3d} - {row['nome']:40s}: {row['total']:7,} viagens")
    
    # Gráfico de ranking
    plt.figure(figsize=(14, 10))
    y_pos = np.arange(len(df))
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(df)))
    bars = plt.barh(y_pos, df['total'], color=colors, alpha=0.8, edgecolor='black')
    
    plt.yticks(y_pos, [f"{row['station_id']} - {row['nome'][:35]}" 
                        for _, row in df.iterrows()], fontsize=9)
    plt.xlabel('Número de Viagens (Saídas + Chegadas)', fontsize=12, fontweight='bold')
    plt.ylabel('Estação', fontsize=12, fontweight='bold')
    plt.title('Ranking de Estações USP por Volume de Viagens', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    # Adicionar valores nas barras
    for i, (bar, total) in enumerate(zip(bars, df['total'])):
        plt.text(bar.get_width() + df['total'].max()*0.01, bar.get_y() + bar.get_height()/2,
                f'{total:,}', va='center', fontsize=8)
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/ranking_estacoes_usp.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Gráfico de balanço (saídas vs chegadas)
    plt.figure(figsize=(14, 10))
    
    df_sorted = df.sort_values('balanco')
    y_pos = np.arange(len(df_sorted))
    colors = ['red' if b < 0 else 'green' for b in df_sorted['balanco']]
    
    plt.barh(y_pos, df_sorted['balanco'], color=colors, alpha=0.7, edgecolor='black')
    plt.yticks(y_pos, [f"{row['station_id']} - {row['nome'][:35]}" 
                        for _, row in df_sorted.iterrows()], fontsize=9)
    plt.xlabel('Balanço (Saídas - Chegadas)', fontsize=12, fontweight='bold')
    plt.ylabel('Estação', fontsize=12, fontweight='bold')
    plt.title('Balanço de Viagens por Estação (Verde = Mais Saídas, Vermelho = Mais Chegadas)', 
              fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='-', linewidth=1)
    plt.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/balanco_estacoes_usp.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../ranking_estacoes_usp.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df

def analise_top5_estacoes_por_hora():
    """Analisa padrão horário das top 5 estações"""
    print("\n" + "="*80)
    print("  ANÁLISE HORÁRIA - TOP 5 ESTAÇÕES")
    print("="*80)
    
    # Obter ranking
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks)
    
    dados_estacoes = []
    for estacao in estacoes_usp:
        total = (Trip.objects.filter(initial_station=estacao).count() + 
                Trip.objects.filter(final_station=estacao).count())
        dados_estacoes.append({
            'station_id': estacao.station_id,
            'nome': estacao.name,
            'total': total,
            'objeto': estacao
        })
    
    df_ranking = pd.DataFrame(dados_estacoes).sort_values('total', ascending=False)
    top5 = df_ranking.head(5)
    
    print(f"\n📊 Analisando TOP 5 estações:")
    for _, row in top5.iterrows():
        print(f"   {row['station_id']:3d} - {row['nome']:40s}: {row['total']:7,} viagens")
    
    # Coletar dados por hora para cada estação
    fig, axes = plt.subplots(5, 1, figsize=(14, 16))
    
    for idx, (_, row) in enumerate(top5.iterrows()):
        estacao = row['objeto']
        
        # Contar saídas e chegadas por hora
        saidas_dict = defaultdict(int)
        chegadas_dict = defaultdict(int)
        
        for viagem in Trip.objects.filter(initial_station=estacao).values('start_hour'):
            if viagem['start_hour'] is not None:
                saidas_dict[viagem['start_hour']] += 1
        
        for viagem in Trip.objects.filter(final_station=estacao).values('end_hour'):
            if viagem['end_hour'] is not None:
                chegadas_dict[viagem['end_hour']] += 1
        
        horas = range(24)
        saidas = [saidas_dict.get(h, 0) for h in horas]
        chegadas = [chegadas_dict.get(h, 0) for h in horas]
        
        # Plotar
        ax = axes[idx]
        width = 0.35
        x = np.arange(24)
        
        ax.bar(x - width/2, saidas, width, label='Saídas', color='steelblue', alpha=0.8, edgecolor='black')
        ax.bar(x + width/2, chegadas, width, label='Chegadas', color='coral', alpha=0.8, edgecolor='black')
        
        ax.set_title(f"{row['station_id']} - {row['nome']} (Total: {row['total']:,} viagens)", 
                    fontweight='bold')
        ax.set_xlabel('Hora do Dia')
        ax.set_ylabel('Número de Viagens')
        ax.set_xticks(x)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Padrão Horário das Top 5 Estações USP', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/top5_estacoes_padrao_horario.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    return top5

def comparacao_grupos_estacoes():
    """Compara grupos de estações por localização/função"""
    print("\n" + "="*80)
    print("  COMPARAÇÃO POR GRUPOS DE ESTAÇÕES")
    print("="*80)
    
    # Definir grupos (baseado em conhecimento do campus)
    grupos = {
        'Entradas/Acessos': [244, 246, 255],  # Metrô Butantã, Portão CPTM, Tiradentes
        'Alimentação': [249, 250],  # Bandejão Central, Bandejão Física
        'Institutos Centrais': [242, 243, 245, 247],  # IME, FEA, P1, Praça do Relógio
        'Institutos Periféricos': [251, 252, 253, 256, 257, 258, 259, 260]
    }
    
    print("\n📊 Grupos definidos:")
    for nome_grupo, ids in grupos.items():
        print(f"   {nome_grupo}: {ids}")
    
    # Calcular totais por grupo
    dados_grupos = []
    for nome_grupo, ids_estacoes in grupos.items():
        estacoes = Station.objects.filter(station_id__in=ids_estacoes)
        total_saidas = sum(Trip.objects.filter(initial_station=e).count() for e in estacoes)
        total_chegadas = sum(Trip.objects.filter(final_station=e).count() for e in estacoes)
        total = total_saidas + total_chegadas
        
        dados_grupos.append({
            'grupo': nome_grupo,
            'estacoes': len(ids_estacoes),
            'viagens_total': total,
            'viagens_por_estacao': total / len(ids_estacoes) if len(ids_estacoes) > 0 else 0
        })
    
    df_grupos = pd.DataFrame(dados_grupos).sort_values('viagens_total', ascending=False)
    
    print(f"\n📊 Estatísticas por grupo:")
    for _, row in df_grupos.iterrows():
        print(f"   {row['grupo']:25s}: {row['viagens_total']:7,} viagens "
              f"({row['viagens_por_estacao']:,.0f} por estação)")
    
    # Gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total por grupo
    colors = plt.cm.Set3(range(len(df_grupos)))
    ax1.bar(df_grupos['grupo'], df_grupos['viagens_total'], color=colors, alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Grupo de Estações', fontweight='bold')
    ax1.set_ylabel('Total de Viagens', fontweight='bold')
    ax1.set_title('Total de Viagens por Grupo de Estações', fontweight='bold')
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(axis='y', alpha=0.3)
    
    # Média por estação
    ax2.bar(df_grupos['grupo'], df_grupos['viagens_por_estacao'], color=colors, alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Grupo de Estações', fontweight='bold')
    ax2.set_ylabel('Média de Viagens por Estação', fontweight='bold')
    ax2.set_title('Média de Viagens por Estação em Cada Grupo', fontweight='bold')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/comparacao_grupos_estacoes.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../grupos_estacoes.csv'
    df_grupos.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df_grupos

def heatmap_estacoes_hora():
    """Gera heatmap de uso por estação e hora"""
    print("\n" + "="*80)
    print("  HEATMAP: ESTAÇÕES vs HORA DO DIA")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    # Matriz: estações x horas
    matriz = []
    nomes_estacoes = []
    
    for estacao in estacoes_usp:
        # Contar viagens (saídas + chegadas) por hora
        viagens_por_hora = [0] * 24
        
        for viagem in Trip.objects.filter(initial_station=estacao).values('start_hour'):
            if viagem['start_hour'] is not None:
                viagens_por_hora[viagem['start_hour']] += 1
        
        for viagem in Trip.objects.filter(final_station=estacao).values('end_hour'):
            if viagem['end_hour'] is not None:
                viagens_por_hora[viagem['end_hour']] += 1
        
        total = sum(viagens_por_hora)
        if total > 0:  # Só incluir estações com viagens
            matriz.append(viagens_por_hora)
            nomes_estacoes.append(f"{estacao.station_id} - {estacao.name[:25]}")
    
    # Criar DataFrame
    df_heatmap = pd.DataFrame(matriz, index=nomes_estacoes, columns=range(24))
    
    print(f"\n📊 Heatmap gerado com {len(nomes_estacoes)} estações")
    
    # Gráfico
    plt.figure(figsize=(16, 12))
    sns.heatmap(df_heatmap, cmap='YlOrRd', annot=False, fmt='d', 
                cbar_kws={'label': 'Número de Viagens'},
                linewidths=0.5, linecolor='gray')
    
    plt.xlabel('Hora do Dia', fontsize=12, fontweight='bold')
    plt.ylabel('Estação', fontsize=12, fontweight='bold')
    plt.title('Heatmap de Uso por Estação e Hora do Dia', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/heatmap_estacoes_hora.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../heatmap_estacoes_hora.csv'
    df_heatmap.to_csv(csv_path, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df_heatmap

def main():
    """Função principal"""
    print("\n" + "🚴" * 40)
    print(" " * 20 + "ANÁLISE POR ESTAÇÃO - BIKESCIENCE USP")
    print(" " * 20 + "Script 03: Análise Individual de Estações")
    print("🚴" * 40)
    
    try:
        ranking_estacoes()
        analise_top5_estacoes_por_hora()
        comparacao_grupos_estacoes()
        heatmap_estacoes_hora()
        
        print("\n" + "=" * 80)
        print("  ✅ ANÁLISE POR ESTAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"  📁 Gráficos salvos em: {OUTPUT_DIR}/")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
