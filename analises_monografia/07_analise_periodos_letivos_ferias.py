#!/usr/bin/env python3
"""
ANÁLISE 2: PERÍODOS LETIVOS vs FÉRIAS ACADÊMICAS
=================================================

Objetivo: Comparar o uso do sistema em períodos letivos vs férias,
mostrando a sazonalidade característica do ambiente universitário.

Contexto USP:
- Janeiro/Fevereiro: Férias de verão (campus praticamente vazio)
- Julho: Recesso de meio de ano
- Dezembro: Férias de fim de ano
- Março-Junho, Agosto-Novembro: Períodos letivos intensos

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
from django.db.models.functions import ExtractYear, ExtractMonth
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

def classificar_periodo(mes):
    """Classifica o mês como letivo ou férias"""
    ferias = [1, 2, 7, 12]  # Jan, Fev, Jul, Dez
    return 'Férias' if mes in ferias else 'Letivo'

def analise_periodos_letivos_ferias():
    """
    Análise principal: Comparação uso mensal e sazonal
    """
    
    print("="*80)
    print("ANÁLISE 2: PERÍODOS LETIVOS vs FÉRIAS ACADÊMICAS")
    print("="*80)
    
    # =================================================================
    # CONSULTA 1: Viagens agrupadas por ano e mês
    # =================================================================
    viagens_mes = Trip.objects.annotate(
        ano=ExtractYear('start_time'),
        mes=ExtractMonth('start_time')
    ).values('ano', 'mes').annotate(
        total_viagens=Count('id'),
        duracao_media=Avg('duration_seconds')
    ).order_by('ano', 'mes')
    
    print_sql_query(
        "Viagens por ano e mês",
        viagens_mes
    )
    
    df = pd.DataFrame(list(viagens_mes))
    
    if df.empty:
        print("❌ Nenhum dado encontrado!")
        return
    
    # Adicionar coluna de classificação
    df['periodo'] = df['mes'].apply(classificar_periodo)
    df['mes_ano'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    
    # =================================================================
    # CONSULTA 2: Viagens apenas nos meses de FÉRIAS
    # =================================================================
    viagens_ferias = Trip.objects.filter(
        month__in=[1, 2, 7, 12]
    ).annotate(
        mes=F('month')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    
    print_sql_query(
        "Viagens nos meses de FÉRIAS (jan, fev, jul, dez)",
        viagens_ferias
    )
    
    # =================================================================
    # CONSULTA 3: Viagens apenas nos meses LETIVOS
    # =================================================================
    viagens_letivo = Trip.objects.exclude(
        month__in=[1, 2, 7, 12]
    ).annotate(
        mes=F('month')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    
    print_sql_query(
        "Viagens nos meses LETIVOS (mar-jun, ago-nov)",
        viagens_letivo
    )
    
    # =================================================================
    # ESTATÍSTICAS RESUMIDAS
    # =================================================================
    total_ferias = df[df['periodo'] == 'Férias']['total_viagens'].sum()
    total_letivo = df[df['periodo'] == 'Letivo']['total_viagens'].sum()
    
    media_mensal_ferias = df[df['periodo'] == 'Férias']['total_viagens'].mean()
    media_mensal_letivo = df[df['periodo'] == 'Letivo']['total_viagens'].mean()
    
    print("\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de viagens em FÉRIAS: {int(total_ferias):,}")
    print(f"   Total de viagens em LETIVO: {int(total_letivo):,}")
    print(f"   Média mensal FÉRIAS: {int(media_mensal_ferias):,} viagens/mês")
    print(f"   Média mensal LETIVO: {int(media_mensal_letivo):,} viagens/mês")
    print(f"   Razão Letivo/Férias: {media_mensal_letivo/media_mensal_ferias if media_mensal_ferias > 0 else 0:.1f}x")
    
    # Identificar mês com menor uso (esperado: férias)
    mes_menor = df.loc[df['total_viagens'].idxmin()]
    mes_maior = df.loc[df['total_viagens'].idxmax()]
    
    print(f"\n📉 MÊS COM MENOR USO:")
    print(f"   {mes_menor['mes_ano']} ({classificar_periodo(mes_menor['mes'])}): {int(mes_menor['total_viagens']):,} viagens")
    
    print(f"\n📈 MÊS COM MAIOR USO:")
    print(f"   {mes_maior['mes_ano']} ({classificar_periodo(mes_maior['mes'])}): {int(mes_maior['total_viagens']):,} viagens")
    
    # =================================================================
    # GRÁFICO 1: Linha temporal com destaque para períodos
    # =================================================================
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Cores diferentes para férias e letivo
    cores = ['#E63946' if p == 'Férias' else '#06A77D' for p in df['periodo']]
    
    ax.bar(range(len(df)), df['total_viagens'], color=cores, alpha=0.8, edgecolor='black')
    ax.plot(range(len(df)), df['total_viagens'], color='black', linewidth=2, marker='o', markersize=5)
    
    # Legendas
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#06A77D', label='Período Letivo'),
        Patch(facecolor='#E63946', label='Férias Acadêmicas')
    ]
    ax.legend(handles=legend_elements, fontsize=11, loc='upper left')
    
    ax.set_title('Viagens por Mês: Períodos Letivos vs Férias Acadêmicas', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Número de Viagens', fontsize=12)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['mes_ano'], rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath1 = os.path.join(OUTPUT_DIR, 'analise_07_periodos_letivos_temporal.png')
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath1}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 2: Comparação média mensal Letivo vs Férias
    # =================================================================
    fig, ax = plt.subplots(figsize=(10, 7))
    
    periodos = ['Letivo', 'Férias']
    medias = [media_mensal_letivo, media_mensal_ferias]
    cores_barras = ['#06A77D', '#E63946']
    
    bars = ax.bar(periodos, medias, color=cores_barras, alpha=0.8, edgecolor='black', width=0.5)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_title('Comparação: Média Mensal de Viagens\nPeríodo Letivo vs Férias', 
                 fontsize=14, fontweight='bold')
    ax.set_ylabel('Média de Viagens por Mês', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Adicionar linha de referência
    ax.axhline(y=media_mensal_letivo, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    plt.tight_layout()
    filepath2 = os.path.join(OUTPUT_DIR, 'analise_07_periodos_letivos_comparacao.png')
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath2}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 3: Boxplot mostrando distribuição
    # =================================================================
    fig, ax = plt.subplots(figsize=(10, 7))
    
    df_letivo = df[df['periodo'] == 'Letivo']['total_viagens']
    df_ferias = df[df['periodo'] == 'Férias']['total_viagens']
    
    bp = ax.boxplot([df_letivo, df_ferias], 
                     labels=['Período Letivo', 'Férias'],
                     patch_artist=True,
                     widths=0.6)
    
    # Colorir boxes
    for patch, color in zip(bp['boxes'], ['#06A77D', '#E63946']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_title('Distribuição de Viagens Mensais: Letivo vs Férias', 
                 fontsize=14, fontweight='bold')
    ax.set_ylabel('Número de Viagens por Mês', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath3 = os.path.join(OUTPUT_DIR, 'analise_07_periodos_letivos_boxplot.png')
    plt.savefig(filepath3, dpi=300, bbox_inches='tight')
    print(f"✅ Boxplot salvo: {filepath3}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 4: Padrão sazonal por mês do ano (agregando anos)
    # =================================================================
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Agrupar por mês (independente do ano)
    viagens_por_mes = df.groupby('mes')['total_viagens'].mean().reset_index()
    viagens_por_mes['periodo'] = viagens_por_mes['mes'].apply(classificar_periodo)
    
    cores_meses = ['#E63946' if classificar_periodo(m) == 'Férias' else '#06A77D' 
                   for m in viagens_por_mes['mes']]
    
    ax.bar(viagens_por_mes['mes'], viagens_por_mes['total_viagens'], 
           color=cores_meses, alpha=0.8, edgecolor='black')
    
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(meses_nomes)
    
    ax.set_title('Padrão Sazonal: Média de Viagens por Mês (todos os anos)', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Média de Viagens', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Legendas
    ax.legend(handles=legend_elements, fontsize=11, loc='upper right')
    
    plt.tight_layout()
    filepath4 = os.path.join(OUTPUT_DIR, 'analise_07_periodos_sazonal.png')
    plt.savefig(filepath4, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico sazonal salvo: {filepath4}")
    plt.close()
    
    # =================================================================
    # SALVAR DADOS TABULARES
    # =================================================================
    csv_path = os.path.join(OUTPUT_DIR, 'analise_07_periodos_letivos_dados.csv')
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Dados salvos: {csv_path}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE 2 CONCLUÍDA!")
    print("="*80)
    
    return {
        'total_ferias': int(total_ferias),
        'total_letivo': int(total_letivo),
        'media_ferias': int(media_mensal_ferias),
        'media_letivo': int(media_mensal_letivo),
        'razao': media_mensal_letivo/media_mensal_ferias if media_mensal_ferias > 0 else 0
    }

if __name__ == '__main__':
    resultado = analise_periodos_letivos_ferias()
    print(f"\n📊 Resumo: Período letivo tem {resultado['razao']:.1f}x mais viagens que férias")
