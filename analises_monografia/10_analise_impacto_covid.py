#!/usr/bin/env python3
"""
ANÁLISE 5: IMPACTO DA PANDEMIA COVID-19
========================================

Objetivo: Analisar a evolução do uso do sistema durante a pandemia,
mostrando lockdown, retorno híbrido e normalização.

Contexto USP:
- Sistema inaugurado em MARÇO 2020 (início da pandemia!)
- 2020: Aulas remotas, campus fechado
- 2021: Retorno híbrido gradual
- 2022: Retorno presencial completo
- Caso de estudo histórico único

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

from django.db.models import Count, Avg, F
from django.db.models.functions import ExtractYear, ExtractMonth, TruncMonth
from ciclovias.models import Trip

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

def classificar_periodo_covid(ano, mes):
    """Classifica o período em relação à pandemia"""
    if ano == 2020:
        return 'Pandemia Inicial'
    elif ano == 2021:
        return 'Retorno Híbrido'
    elif ano >= 2022:
        return 'Presencial'
    else:
        return 'Pré-Pandemia'

def analise_impacto_covid():
    """
    Análise principal: Evolução temporal durante COVID-19
    """
    
    print("="*80)
    print("ANÁLISE 5: IMPACTO DA PANDEMIA COVID-19")
    print("="*80)
    
    # =================================================================
    # CONSULTA 1: Período completo de dados disponíveis
    # =================================================================
    primeira_viagem = Trip.objects.order_by('start_time').first()
    ultima_viagem = Trip.objects.order_by('-start_time').first()
    
    if primeira_viagem and ultima_viagem:
        print(f"\n📅 PERÍODO DOS DADOS:")
        print(f"   Primeira viagem: {primeira_viagem.start_time.strftime('%Y-%m-%d')}")
        print(f"   Última viagem: {ultima_viagem.start_time.strftime('%Y-%m-%d')}")
        print(f"   Duração: {(ultima_viagem.start_time - primeira_viagem.start_time).days} dias")
    
    # =================================================================
    # CONSULTA 2: Viagens por ano e mês
    # =================================================================
    viagens_mes_ano = Trip.objects.annotate(
        ano=ExtractYear('start_time'),
        mes=ExtractMonth('start_time')
    ).values('ano', 'mes').annotate(
        total_viagens=Count('id'),
        duracao_media=Avg('duration_seconds')
    ).order_by('ano', 'mes')
    
    print_sql_query(
        "Viagens por ano e mês (evolução temporal)",
        viagens_mes_ano
    )
    
    df = pd.DataFrame(list(viagens_mes_ano))
    
    if df.empty:
        print("❌ Nenhum dado encontrado!")
        return {}
    
    # Adicionar colunas de classificação
    df['periodo_covid'] = df.apply(lambda x: classificar_periodo_covid(x['ano'], x['mes']), axis=1)
    
    # Preparar dataframe para conversão de data (renomear colunas para inglês)
    df_date = df[['ano', 'mes']].copy()
    df_date.columns = ['year', 'month']
    df_date['day'] = 1
    df['mes_ano'] = pd.to_datetime(df_date)
    
    df['mes_ano_str'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    
    # =================================================================
    # CONSULTA 3: Total por ano
    # =================================================================
    viagens_ano = Trip.objects.annotate(
        ano=ExtractYear('start_time')
    ).values('ano').annotate(
        total=Count('id')
    ).order_by('ano')
    
    print_sql_query(
        "Total de viagens por ano",
        viagens_ano
    )
    
    df_ano = pd.DataFrame(list(viagens_ano))
    
    # =================================================================
    # CONSULTA 4: Comparar mesmos meses em anos diferentes
    # =================================================================
    print(f"\n📊 COMPARAÇÃO ENTRE ANOS (mesmo mês):")
    print(f"\n{'Mês':<15} {'2020':>12} {'2021':>12} {'2022':>12} {'2023':>12}")
    print("-" * 67)
    
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    for mes_num in range(1, 13):
        linha = f"{meses_nomes[mes_num-1]:<15}"
        for ano in [2020, 2021, 2022, 2023]:
            viagens = df[(df['ano'] == ano) & (df['mes'] == mes_num)]['total_viagens'].sum()
            if viagens > 0:
                linha += f" {int(viagens):>12,}"
            else:
                linha += f" {'-':>12}"
        print(linha)
    
    # =================================================================
    # ESTATÍSTICAS POR PERÍODO
    # =================================================================
    print(f"\n📈 ESTATÍSTICAS POR PERÍODO COVID:")
    
    for periodo in ['Pandemia Inicial', 'Retorno Híbrido', 'Presencial']:
        dados_periodo = df[df['periodo_covid'] == periodo]
        if not dados_periodo.empty:
            total = dados_periodo['total_viagens'].sum()
            media_mensal = dados_periodo['total_viagens'].mean()
            meses = len(dados_periodo)
            
            print(f"\n   {periodo}:")
            print(f"      Total de viagens: {int(total):,}")
            print(f"      Média mensal: {int(media_mensal):,}")
            print(f"      Número de meses: {meses}")
    
    # Crescimento relativo
    if not df_ano.empty and len(df_ano) > 1:
        print(f"\n📊 CRESCIMENTO ANUAL:")
        for i in range(1, len(df_ano)):
            ano_anterior = df_ano.iloc[i-1]
            ano_atual = df_ano.iloc[i]
            crescimento = ((ano_atual['total'] - ano_anterior['total']) / ano_anterior['total'] * 100)
            print(f"   {int(ano_anterior['ano'])} → {int(ano_atual['ano'])}: {crescimento:+.1f}% ({int(ano_anterior['total']):,} → {int(ano_atual['total']):,} viagens)")
    
    # =================================================================
    # GRÁFICO 1: Evolução temporal mensal
    # =================================================================
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Cores por período
    cores_periodo = {
        'Pandemia Inicial': '#E63946',
        'Retorno Híbrido': '#F77F00',
        'Presencial': '#06A77D',
        'Pré-Pandemia': '#457B9D'
    }
    
    cores = [cores_periodo.get(p, '#999999') for p in df['periodo_covid']]
    
    ax.bar(range(len(df)), df['total_viagens'], color=cores, alpha=0.8, edgecolor='black', width=0.8)
    ax.plot(range(len(df)), df['total_viagens'], color='black', linewidth=2, marker='o', markersize=4)
    
    # Legendas
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E63946', label='Pandemia Inicial (2020)'),
        Patch(facecolor='#F77F00', label='Retorno Híbrido (2021)'),
        Patch(facecolor='#06A77D', label='Presencial (2022+)')
    ]
    ax.legend(handles=legend_elements, fontsize=11, loc='upper left')
    
    ax.set_title('Evolução do Uso Durante a Pandemia COVID-19', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Número de Viagens', fontsize=12)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['mes_ano_str'], rotation=45, ha='right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    
    # Adicionar anotações de eventos importantes
    if primeira_viagem:
        inicio = primeira_viagem.start_time
        if inicio.year == 2020 and inicio.month == 3:
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, linewidth=2)
            ax.text(0, ax.get_ylim()[1]*0.95, 'Início\nPandemia', 
                   ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    filepath1 = os.path.join(OUTPUT_DIR, 'analise_10_covid_evolucao_temporal.png')
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath1}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 2: Comparação anual (barras agrupadas)
    # =================================================================
    if not df_ano.empty and len(df_ano) > 1:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        anos = df_ano['ano'].astype(int).tolist()
        totais = df_ano['total'].tolist()
        
        cores_anos = []
        for ano in anos:
            if ano == 2020:
                cores_anos.append('#E63946')
            elif ano == 2021:
                cores_anos.append('#F77F00')
            else:
                cores_anos.append('#06A77D')
        
        bars = ax.bar(range(len(anos)), totais, color=cores_anos, alpha=0.8, edgecolor='black', width=0.6)
        
        # Adicionar valores nas barras
        for i, (bar, total) in enumerate(zip(bars, totais)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(total):,}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_title('Comparação Anual: Impacto da Pandemia e Recuperação', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Ano', fontsize=12)
        ax.set_ylabel('Total de Viagens', fontsize=12)
        ax.set_xticks(range(len(anos)))
        ax.set_xticklabels(anos, fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        filepath2 = os.path.join(OUTPUT_DIR, 'analise_10_covid_comparacao_anual.png')
        plt.savefig(filepath2, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico salvo: {filepath2}")
        plt.close()
    
    # =================================================================
    # GRÁFICO 3: Heatmap de viagens por mês e ano
    # =================================================================
    if len(df['ano'].unique()) > 1:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Criar pivot table
        pivot_data = df.pivot_table(
            values='total_viagens',
            index='mes',
            columns='ano',
            fill_value=0
        )
        
        sns.heatmap(pivot_data, 
                   annot=True, 
                   fmt=',.0f', 
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Número de Viagens'},
                   ax=ax,
                   linewidths=0.5)
        
        ax.set_title('Heatmap: Viagens por Mês e Ano (Evolução durante COVID-19)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Ano', fontsize=12)
        ax.set_ylabel('Mês', fontsize=12)
        ax.set_yticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], rotation=0)
        
        plt.tight_layout()
        filepath3 = os.path.join(OUTPUT_DIR, 'analise_10_covid_heatmap.png')
        plt.savefig(filepath3, dpi=300, bbox_inches='tight')
        print(f"✅ Heatmap salvo: {filepath3}")
        plt.close()
    
    # =================================================================
    # GRÁFICO 4: Taxa de recuperação (normalizado)
    # =================================================================
    if len(df) > 12:  # Se tiver mais de 1 ano de dados
        fig, ax = plt.subplots(figsize=(16, 7))
        
        # Normalizar em relação ao máximo
        max_viagens = df['total_viagens'].max()
        df['percentual_max'] = (df['total_viagens'] / max_viagens * 100)
        
        ax.plot(range(len(df)), df['percentual_max'], 
               color='#2E86AB', linewidth=3, marker='o', markersize=6)
        ax.fill_between(range(len(df)), df['percentual_max'], alpha=0.3, color='#2E86AB')
        
        # Linha de referência
        ax.axhline(y=100, color='green', linestyle='--', alpha=0.5, linewidth=2, label='100% (máximo)')
        ax.axhline(y=50, color='orange', linestyle='--', alpha=0.5, linewidth=1, label='50%')
        
        ax.set_title('Taxa de Recuperação do Sistema (% em relação ao pico)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês', fontsize=12)
        ax.set_ylabel('Percentual em relação ao máximo (%)', fontsize=12)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['mes_ano_str'], rotation=45, ha='right', fontsize=9)
        ax.set_ylim(0, 110)
        ax.legend(fontsize=11)
        ax.grid(axis='both', alpha=0.3)
        
        plt.tight_layout()
        filepath4 = os.path.join(OUTPUT_DIR, 'analise_10_covid_taxa_recuperacao.png')
        plt.savefig(filepath4, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico salvo: {filepath4}")
        plt.close()
    
    # =================================================================
    # SALVAR DADOS TABULARES
    # =================================================================
    csv_path = os.path.join(OUTPUT_DIR, 'analise_10_covid_dados.csv')
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Dados salvos: {csv_path}")
    
    csv_path_ano = os.path.join(OUTPUT_DIR, 'analise_10_covid_dados_anuais.csv')
    if not df_ano.empty:
        df_ano.to_csv(csv_path_ano, index=False)
        print(f"✅ Dados anuais salvos: {csv_path_ano}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE 5 CONCLUÍDA!")
    print("="*80)
    
    # Calcular taxa de recuperação
    if not df_ano.empty and len(df_ano) > 1:
        ano_inicial = df_ano.iloc[0]['total']
        ano_final = df_ano.iloc[-1]['total']
        recuperacao = ((ano_final - ano_inicial) / ano_inicial * 100) if ano_inicial > 0 else 0
    else:
        recuperacao = 0
    
    return {
        'total_2020': int(df_ano[df_ano['ano'] == 2020]['total'].sum()) if not df_ano.empty else 0,
        'total_2021': int(df_ano[df_ano['ano'] == 2021]['total'].sum()) if not df_ano.empty else 0,
        'total_2022': int(df_ano[df_ano['ano'] == 2022]['total'].sum()) if not df_ano.empty else 0,
        'taxa_recuperacao': recuperacao
    }

if __name__ == '__main__':
    resultado = analise_impacto_covid()
    if resultado:
        print(f"\n📊 Resumo: 2020→2022 mostrou recuperação de {resultado['taxa_recuperacao']:.1f}%")
