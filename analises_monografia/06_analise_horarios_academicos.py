#!/usr/bin/env python3
"""
ANÁLISE 1: PADRÕES DE HORÁRIOS ACADÊMICOS USP
==============================================

Objetivo: Identificar picos de uso nos horários típicos de aula da USP
(8h, 10h, 14h, 16h, 19h) e comparar dias úteis vs fins de semana.

Contexto USP:
- Aulas começam tipicamente em horários fixos
- Esperamos picos marcados nos inícios/términos de aula
- Fins de semana devem ter padrão muito diferente (uso recreacional)

Consultas SQL documentadas para verificação do professor.
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db.models import Count, Q
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

def analise_horarios_academicos():
    """
    Análise principal: Distribuição de viagens por hora do dia
    comparando dias úteis (seg-sex) vs fins de semana (sab-dom)
    """
    
    print("="*80)
    print("ANÁLISE 1: PADRÕES DE HORÁRIOS ACADÊMICOS USP")
    print("="*80)
    
    # =================================================================
    # CONSULTA 1: Viagens por hora - DIAS ÚTEIS (Segunda a Sexta)
    # =================================================================
    viagens_semana = Trip.objects.filter(
        start_day__in=[0, 1, 2, 3, 4]  # 0=Segunda, 4=Sexta
    ).values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    print_sql_query(
        "Viagens por hora em DIAS ÚTEIS (seg-sex)",
        viagens_semana
    )
    
    # =================================================================
    # CONSULTA 2: Viagens por hora - FINS DE SEMANA (Sábado e Domingo)
    # =================================================================
    viagens_fds = Trip.objects.filter(
        start_day__in=[5, 6]  # 5=Sábado, 6=Domingo
    ).values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    print_sql_query(
        "Viagens por hora em FINS DE SEMANA (sab-dom)",
        viagens_fds
    )
    
    # Converter para DataFrames
    df_semana = pd.DataFrame(list(viagens_semana))
    df_fds = pd.DataFrame(list(viagens_fds))
    
    # Criar array completo de 0-23 horas
    horas = np.arange(0, 24)
    
    # Preparar dados para plotagem
    viagens_por_hora_semana = np.zeros(24)
    viagens_por_hora_fds = np.zeros(24)
    
    if not df_semana.empty:
        for _, row in df_semana.iterrows():
            viagens_por_hora_semana[int(row['start_hour'])] = row['total']
    
    if not df_fds.empty:
        for _, row in df_fds.iterrows():
            viagens_por_hora_fds[int(row['start_hour'])] = row['total']
    
    # =================================================================
    # ESTATÍSTICAS RESUMIDAS
    # =================================================================
    total_semana = int(viagens_por_hora_semana.sum())
    total_fds = int(viagens_por_hora_fds.sum())
    
    print("\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de viagens em dias úteis: {total_semana:,}")
    print(f"   Total de viagens em fins de semana: {total_fds:,}")
    print(f"   Razão semana/FDS: {total_semana/total_fds if total_fds > 0 else 0:.1f}x")
    
    # Identificar horários de pico
    hora_pico_semana = horas[np.argmax(viagens_por_hora_semana)]
    hora_pico_fds = horas[np.argmax(viagens_por_hora_fds)] if total_fds > 0 else 0
    
    print(f"\n⏰ HORÁRIOS DE PICO:")
    print(f"   Dias úteis: {hora_pico_semana}h ({int(viagens_por_hora_semana[hora_pico_semana]):,} viagens)")
    print(f"   Fins de semana: {hora_pico_fds}h ({int(viagens_por_hora_fds[hora_pico_fds]):,} viagens)")
    
    # Verificar picos nos horários acadêmicos (8h, 10h, 14h, 16h, 19h)
    horarios_academicos = [8, 10, 14, 16, 19]
    print(f"\n🎓 VIAGENS NOS HORÁRIOS TÍPICOS DE AULA:")
    for hora in horarios_academicos:
        viagens = int(viagens_por_hora_semana[hora])
        percentual = (viagens / total_semana * 100) if total_semana > 0 else 0
        print(f"   {hora:2d}h: {viagens:6,} viagens ({percentual:5.2f}%)")
    
    # =================================================================
    # GRÁFICO 1: Comparação Semana vs Fim de Semana
    # =================================================================
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Subplot 1: Dias úteis
    ax1.bar(horas, viagens_por_hora_semana, color='#2E86AB', alpha=0.8, edgecolor='black')
    ax1.axvline(x=8, color='red', linestyle='--', alpha=0.5, label='Horários de aula típicos')
    ax1.axvline(x=10, color='red', linestyle='--', alpha=0.5)
    ax1.axvline(x=14, color='red', linestyle='--', alpha=0.5)
    ax1.axvline(x=16, color='red', linestyle='--', alpha=0.5)
    ax1.axvline(x=19, color='red', linestyle='--', alpha=0.5)
    ax1.set_title('Distribuição de Viagens por Hora - DIAS ÚTEIS (Seg-Sex)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Hora do Dia', fontsize=12)
    ax1.set_ylabel('Número de Viagens', fontsize=12)
    ax1.set_xticks(horas)
    ax1.grid(axis='y', alpha=0.3)
    ax1.legend()
    
    # Subplot 2: Fins de semana
    ax2.bar(horas, viagens_por_hora_fds, color='#A23B72', alpha=0.8, edgecolor='black')
    ax2.set_title('Distribuição de Viagens por Hora - FINS DE SEMANA (Sáb-Dom)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Hora do Dia', fontsize=12)
    ax2.set_ylabel('Número de Viagens', fontsize=12)
    ax2.set_xticks(horas)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath1 = os.path.join(OUTPUT_DIR, 'analise_06_horarios_academicos_comparacao.png')
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath1}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 2: Sobreposição para comparação direta
    # =================================================================
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = np.arange(24)
    width = 0.35
    
    ax.bar(x - width/2, viagens_por_hora_semana, width, 
           label='Dias Úteis', color='#2E86AB', alpha=0.8, edgecolor='black')
    ax.bar(x + width/2, viagens_por_hora_fds, width,
           label='Fins de Semana', color='#A23B72', alpha=0.8, edgecolor='black')
    
    # Marcar horários acadêmicos
    for hora in horarios_academicos:
        ax.axvline(x=hora, color='red', linestyle='--', alpha=0.3, linewidth=1)
    
    ax.set_title('Comparação: Dias Úteis vs Fins de Semana - Viagens por Hora', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Hora do Dia', fontsize=12)
    ax.set_ylabel('Número de Viagens', fontsize=12)
    ax.set_xticks(horas)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    filepath2 = os.path.join(OUTPUT_DIR, 'analise_06_horarios_academicos_sobreposicao.png')
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath2}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 3: Heatmap por dia da semana e hora
    # =================================================================
    print("\n🔍 Gerando heatmap detalhado por dia da semana...")
    
    viagens_dia_hora = Trip.objects.values('start_day', 'start_hour').annotate(
        total=Count('id')
    ).order_by('start_day', 'start_hour')
    
    print_sql_query(
        "Viagens por dia da semana e hora (para heatmap)",
        viagens_dia_hora
    )
    
    # Criar matriz 7x24
    heatmap_data = np.zeros((7, 24))
    for item in viagens_dia_hora:
        if item['start_day'] is not None and item['start_hour'] is not None:
            heatmap_data[item['start_day']][item['start_hour']] = item['total']
    
    # Plotar heatmap
    fig, ax = plt.subplots(figsize=(16, 6))
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    sns.heatmap(heatmap_data, 
                annot=False, 
                fmt='g', 
                cmap='YlOrRd', 
                xticklabels=horas,
                yticklabels=dias_semana,
                cbar_kws={'label': 'Número de Viagens'},
                ax=ax)
    
    ax.set_title('Heatmap: Distribuição de Viagens por Dia da Semana e Hora', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Hora do Dia', fontsize=12)
    ax.set_ylabel('Dia da Semana', fontsize=12)
    
    plt.tight_layout()
    filepath3 = os.path.join(OUTPUT_DIR, 'analise_06_horarios_academicos_heatmap.png')
    plt.savefig(filepath3, dpi=300, bbox_inches='tight')
    print(f"✅ Heatmap salvo: {filepath3}")
    plt.close()
    
    # =================================================================
    # SALVAR DADOS TABULARES
    # =================================================================
    df_resultado = pd.DataFrame({
        'hora': horas,
        'viagens_dias_uteis': viagens_por_hora_semana.astype(int),
        'viagens_fds': viagens_por_hora_fds.astype(int),
        'diferenca_absoluta': (viagens_por_hora_semana - viagens_por_hora_fds).astype(int)
    })
    
    csv_path = os.path.join(OUTPUT_DIR, 'analise_06_horarios_academicos_dados.csv')
    df_resultado.to_csv(csv_path, index=False)
    print(f"\n✅ Dados salvos: {csv_path}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE 1 CONCLUÍDA!")
    print("="*80)
    
    return {
        'total_semana': total_semana,
        'total_fds': total_fds,
        'hora_pico_semana': hora_pico_semana,
        'hora_pico_fds': hora_pico_fds
    }

if __name__ == '__main__':
    resultado = analise_horarios_academicos()
    print(f"\n📊 Resumo: {resultado['total_semana']:,} viagens em dias úteis vs {resultado['total_fds']:,} em fins de semana")
