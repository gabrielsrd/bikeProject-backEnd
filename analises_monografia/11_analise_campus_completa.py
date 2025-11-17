#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE COMPLETA DO CAMPUS USP - VERSÃO FOCADA
===============================================

Este script refaz as análises da Seção 5.8 usando EXCLUSIVAMENTE o dataset
de 92.737 viagens do campus (origem OU destino nas 19 estações USP).

Análises implementadas:
1. Horários acadêmicos (8h, 10h, 14h, 16h, 19h) - Campus only
2. Duração média das 63.598 viagens internas
3. Análise de "maré" nos portais (244-Metrô, 246-CPTM, 245-P1)
4. Origens para bandejões no horário de almoço (11h-14h)
5. Correlação com horários de aula USP

Autor: Gabriel + GitHub Copilot
Data: Novembro 2025
"""

import os
import sys
import django
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configuração do Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db.models import Count, Avg, Q, F
from ciclovias.models import Trip, Station

# Configurações de plot
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11

# Diretório de saída
OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# PKs internos das 17 estações USP (CORRETO - Nov 2025)
# EXCLUI: 244-Metrô Butantã e 255-Tiradentes (fora do campus)
ESTACOES_USP = [
    56826,  # 242 - Letras
    56659,  # 243 - Bancos/Reitoria
    48848,  # 245 - P1
    38637,  # 246 - Portão CPTM
    37915,  # 247 - CEPE
    48852,  # 248 - Biblioteca Brasiliana
    38476,  # 249 - Bandejão Central
    56642,  # 250 - Bandejão Química
    38582,  # 251 - FAU
    56762,  # 252 - Psicologia
    38425,  # 253 - Pedalusp Biênio
    56965,  # 254 - Terminal de Ônibus USP
    56713,  # 256 - Bandejão Prefeitura
    56654,  # 257 - Hospital Universitário
    56640,  # 258 - Odontologia
    44878,  # 259 - Vila Indiana
    42323,  # 260 - P3
]

# Estações-portal (pontos de entrada/saída no LIMITE do campus)
ESTACOES_PORTAL = {
    38637: 'PORTÃO CPTM',      # 246
    48848: 'P1',               # 245
    44878: 'Vila Indiana',     # 259
}

ESTACOES_BANDEJAO = {
    38476: 'Bandejão Central',        # 249
    56642: 'Bandejão Química',        # 250
    56713: 'Bandejão Prefeitura'      # 256
}

# Horários de aula USP
HORARIOS_AULA = [8, 10, 14, 16, 19]

def print_sql_query(description, queryset):
    """Imprime a query SQL para documentação."""
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")
    print(queryset.query)
    print(f"{'='*80}\n")


def get_viagens_campus():
    """Retorna queryset com as 92.737 viagens do campus (origem OU destino na USP)."""
    viagens = Trip.objects.filter(
        Q(initial_station_id__in=ESTACOES_USP) | 
        Q(final_station_id__in=ESTACOES_USP)
    )
    print_sql_query("Viagens do campus USP (origem OU destino na USP)", viagens)
    return viagens


def get_viagens_internas():
    """Retorna queryset com as 63.598 viagens internas (origem E destino na USP)."""
    viagens = Trip.objects.filter(
        initial_station_id__in=ESTACOES_USP,
        final_station_id__in=ESTACOES_USP
    )
    print_sql_query("Viagens INTERNAS do campus (origem E destino na USP)", viagens)
    return viagens


def analise_1_horarios_academicos():
    """
    ANÁLISE 1: Horários Acadêmicos
    Foca nas 92.737 viagens do campus, correlacionando com horários de aula USP.
    """
    print("\n" + "="*80)
    print("ANÁLISE 1: HORÁRIOS ACADÊMICOS - DATASET CAMPUS (92.737 viagens)")
    print("="*80)
    
    viagens_campus = get_viagens_campus()
    total_campus = viagens_campus.count()
    
    # Viagens por hora
    por_hora = viagens_campus.values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    print_sql_query("Viagens do campus por hora", por_hora)
    
    df_hora = pd.DataFrame(list(por_hora))
    
    # Estatísticas nos horários de aula
    print(f"\n📊 TOTAL DE VIAGENS DO CAMPUS: {total_campus:,}")
    print(f"\n🎓 VIAGENS NOS HORÁRIOS TÍPICOS DE AULA USP:")
    
    for hora in HORARIOS_AULA:
        viagens_hora = df_hora[df_hora['start_hour'] == hora]['total'].values
        if len(viagens_hora) > 0:
            count = viagens_hora[0]
            pct = (count / total_campus) * 100
            print(f"   {hora:2d}h: {count:6,} viagens ({pct:5.2f}%)")
    
    # Verificar picos 15 minutos antes (usando hora anterior como proxy)
    print(f"\n⏰ VERIFICAÇÃO DE PICOS PRÉ-AULA:")
    for hora in HORARIOS_AULA:
        hora_antes = hora - 1
        if hora_antes >= 0:
            viagens_antes = df_hora[df_hora['start_hour'] == hora_antes]['total'].values
            viagens_hora = df_hora[df_hora['start_hour'] == hora]['total'].values
            if len(viagens_antes) > 0 and len(viagens_hora) > 0:
                diff = viagens_hora[0] - viagens_antes[0]
                print(f"   {hora_antes}h→{hora}h: {diff:+6,} viagens")
    
    # Horário de pico
    hora_pico = df_hora.loc[df_hora['total'].idxmax()]
    print(f"\n📈 HORÁRIO DE PICO: {int(hora_pico['start_hour'])}h com {hora_pico['total']:,} viagens ({hora_pico['total']/total_campus*100:.1f}%)")
    
    # Gráfico 1: Distribuição horária com destaque para horários de aula
    fig, ax = plt.subplots(figsize=(16, 8))
    
    cores = ['#d62728' if h in HORARIOS_AULA else '#1f77b4' for h in df_hora['start_hour']]
    
    ax.bar(df_hora['start_hour'], df_hora['total'], color=cores, alpha=0.7, edgecolor='black')
    
    # Linha de destaque nos horários de aula
    for hora in HORARIOS_AULA:
        ax.axvline(x=hora, color='red', linestyle='--', alpha=0.3, linewidth=2)
    
    ax.set_xlabel('Hora do Dia', fontsize=14, fontweight='bold')
    ax.set_ylabel('Número de Viagens', fontsize=14, fontweight='bold')
    ax.set_title('Distribuição Horária das Viagens do Campus USP\n(Horários de aula destacados em vermelho)', 
                 fontsize=16, fontweight='bold')
    ax.set_xticks(range(0, 24))
    ax.grid(axis='y', alpha=0.3)
    
    # Anotações nos horários de aula
    for hora in HORARIOS_AULA:
        viagens = df_hora[df_hora['start_hour'] == hora]['total'].values[0]
        ax.text(hora, viagens + 200, f'{viagens:,}', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/analise_11_campus_horarios_academicos.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: analise_11_campus_horarios_academicos.png")
    plt.close()
    
    # Salvar dados
    df_hora.to_csv(f'{OUTPUT_DIR}/analise_11_campus_horarios_dados.csv', index=False)
    print(f"✅ Dados salvos: analise_11_campus_horarios_dados.csv")
    
    return df_hora


def analise_2_duracao_viagens_internas():
    """
    ANÁLISE 2: Duração das Viagens Internas
    Calcula duração média das 63.598 viagens internas para verificar
    se é compatível com 'última milha' (curto) ou transporte entre unidades (médio).
    """
    print("\n" + "="*80)
    print("ANÁLISE 2: DURAÇÃO DAS VIAGENS INTERNAS (63.598 viagens)")
    print("="*80)
    
    viagens_internas = get_viagens_internas()
    
    # Estatísticas de duração
    stats = viagens_internas.aggregate(
        total=Count('id'),
        duracao_media=Avg('duration_seconds'),
        duracao_mediana=Avg('duration_seconds')  # Será calculada com pandas
    )
    
    print_sql_query("Estatísticas de duração das viagens internas", viagens_internas)
    
    # Pegar dados para análise detalhada
    duracoes = list(viagens_internas.values_list('duration_seconds', flat=True))
    df_duracoes = pd.DataFrame(duracoes, columns=['duracao_segundos'])
    df_duracoes['duracao_minutos'] = df_duracoes['duracao_segundos'] / 60
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS DE DURAÇÃO:")
    print(f"   Total de viagens internas: {len(duracoes):,}")
    print(f"   Duração média: {np.mean(duracoes)/60:.1f} minutos ({np.mean(duracoes):.0f} segundos)")
    print(f"   Duração mediana: {np.median(duracoes)/60:.1f} minutos ({np.median(duracoes):.0f} segundos)")
    print(f"   Desvio padrão: {np.std(duracoes)/60:.1f} minutos")
    print(f"   Mínimo: {np.min(duracoes)/60:.1f} minutos")
    print(f"   Máximo: {np.max(duracoes)/60:.1f} minutos")
    
    # Quartis
    q25 = np.percentile(duracoes, 25)
    q75 = np.percentile(duracoes, 75)
    print(f"   Q1 (25%): {q25/60:.1f} minutos")
    print(f"   Q3 (75%): {q75/60:.1f} minutos")
    
    # Classificação por duração
    curtas = len([d for d in duracoes if d < 600])  # < 10 min
    medias = len([d for d in duracoes if 600 <= d < 1800])  # 10-30 min
    longas = len([d for d in duracoes if d >= 1800])  # >= 30 min
    
    print(f"\n🚴 CLASSIFICAÇÃO POR DURAÇÃO:")
    print(f"   Curtas (< 10 min): {curtas:,} ({curtas/len(duracoes)*100:.1f}%) - ÚLTIMA MILHA")
    print(f"   Médias (10-30 min): {medias:,} ({medias/len(duracoes)*100:.1f}%) - TRANSPORTE ENTRE UNIDADES")
    print(f"   Longas (>= 30 min): {longas:,} ({longas/len(duracoes)*100:.1f}%) - LAZER/OUTROS")
    
    # Interpretação
    print(f"\n💡 INTERPRETAÇÃO:")
    if np.mean(duracoes) < 600:
        print(f"   ✅ Duração média < 10 min → Compatível com ÚLTIMA MILHA")
    elif np.mean(duracoes) < 1800:
        print(f"   ✅ Duração média 10-30 min → Compatível com TRANSPORTE ENTRE UNIDADES")
    else:
        print(f"   ⚠️  Duração média > 30 min → Uso predominante para LAZER/OUTROS")
    
    # Gráfico: Histograma de durações
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Histograma
    ax1.hist(df_duracoes['duracao_minutos'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(x=np.mean(duracoes)/60, color='red', linestyle='--', linewidth=2, label=f'Média: {np.mean(duracoes)/60:.1f} min')
    ax1.axvline(x=np.median(duracoes)/60, color='green', linestyle='--', linewidth=2, label=f'Mediana: {np.median(duracoes)/60:.1f} min')
    ax1.axvline(x=10, color='orange', linestyle=':', linewidth=2, alpha=0.5, label='10 min (última milha)')
    ax1.axvline(x=30, color='purple', linestyle=':', linewidth=2, alpha=0.5, label='30 min (limite transporte)')
    ax1.set_xlabel('Duração (minutos)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Número de Viagens', fontsize=12, fontweight='bold')
    ax1.set_title('Distribuição de Duração das Viagens Internas do Campus', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Boxplot
    ax2.boxplot(df_duracoes['duracao_minutos'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightblue', alpha=0.7),
                medianprops=dict(color='red', linewidth=2))
    ax2.set_ylabel('Duração (minutos)', fontsize=12, fontweight='bold')
    ax2.set_title('Boxplot de Duração', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/analise_11_campus_duracao_viagens.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: analise_11_campus_duracao_viagens.png")
    plt.close()
    
    # Salvar dados
    df_duracoes.describe().to_csv(f'{OUTPUT_DIR}/analise_11_campus_duracao_stats.csv')
    print(f"✅ Estatísticas salvas: analise_11_campus_duracao_stats.csv")


def analise_3_mare_portais():
    """
    ANÁLISE 3: Análise de "Maré" nos Portais
    Gera gráfico de 24 horas mostrando saldo líquido (Partidas - Chegadas)
    nas estações-portal: 244-Metrô, 246-CPTM, 245-P1.
    """
    print("\n" + "="*80)
    print("ANÁLISE 3: PADRÃO DE 'MARÉ' NOS PORTAIS (244, 246, 245)")
    print("="*80)
    
    viagens_campus = get_viagens_campus()
    
    resultados = {}
    
    for estacao_id, nome in ESTACOES_PORTAL.items():
        print(f"\n🚪 Analisando portal: {nome} (ID {estacao_id})")
        
        # Partidas (saídas) do portal
        partidas = viagens_campus.filter(
            initial_station_id=estacao_id
        ).values('start_hour').annotate(
            total=Count('id')
        ).order_by('start_hour')
        
        print_sql_query(f"Partidas do portal {nome} por hora", partidas)
        
        # Chegadas ao portal
        chegadas = viagens_campus.filter(
            final_station_id=estacao_id
        ).values('start_hour').annotate(
            total=Count('id')
        ).order_by('start_hour')
        
        print_sql_query(f"Chegadas ao portal {nome} por hora", chegadas)
        
        df_partidas = pd.DataFrame(list(partidas))
        df_chegadas = pd.DataFrame(list(chegadas))
        
        # Criar dataframe completo (0-23h)
        df_completo = pd.DataFrame({'hora': range(24)})
        df_completo = df_completo.merge(
            df_partidas.rename(columns={'start_hour': 'hora', 'total': 'partidas'}),
            on='hora', how='left'
        )
        df_completo = df_completo.merge(
            df_chegadas.rename(columns={'start_hour': 'hora', 'total': 'chegadas'}),
            on='hora', how='left'
        )
        df_completo = df_completo.fillna(0)
        
        # Saldo = Partidas - Chegadas
        # Saldo > 0: Mais gente SAINDO do portal (entrando no campus)
        # Saldo < 0: Mais gente CHEGANDO ao portal (saindo do campus)
        df_completo['saldo'] = df_completo['partidas'] - df_completo['chegadas']
        
        resultados[estacao_id] = {
            'nome': nome,
            'df': df_completo
        }
        
        # Estatísticas
        print(f"   Total partidas: {df_completo['partidas'].sum():,.0f}")
        print(f"   Total chegadas: {df_completo['chegadas'].sum():,.0f}")
        print(f"   Saldo total: {df_completo['saldo'].sum():+,.0f}")
        print(f"   Hora de maior entrada: {df_completo.loc[df_completo['saldo'].idxmax(), 'hora']:.0f}h (saldo: {df_completo['saldo'].max():+,.0f})")
        print(f"   Hora de maior saída: {df_completo.loc[df_completo['saldo'].idxmin(), 'hora']:.0f}h (saldo: {df_completo['saldo'].min():+,.0f})")
    
    # Gráfico comparativo (3 portais)
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    for i, (estacao_id, dados) in enumerate(resultados.items()):
        ax = axes[i]
        df = dados['df']
        nome = dados['nome']
        
        # Cores: verde para entrada (saldo +), vermelho para saída (saldo -)
        cores = ['green' if s > 0 else 'red' for s in df['saldo']]
        
        ax.bar(df['hora'], df['saldo'], color=cores, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax.set_xlabel('Hora do Dia', fontsize=12, fontweight='bold')
        ax.set_ylabel('Saldo (Partidas - Chegadas)', fontsize=12, fontweight='bold')
        ax.set_title(f'Padrão de "Maré" - {nome}\n(Verde: entrada no campus | Vermelho: saída do campus)', 
                     fontsize=13, fontweight='bold')
        ax.set_xticks(range(0, 24))
        ax.grid(axis='y', alpha=0.3)
        
        # Destacar horários de pico
        hora_max_entrada = df.loc[df['saldo'].idxmax(), 'hora']
        hora_max_saida = df.loc[df['saldo'].idxmin(), 'hora']
        ax.axvline(x=hora_max_entrada, color='green', linestyle='--', alpha=0.5)
        ax.axvline(x=hora_max_saida, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/analise_11_campus_mare_portais.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: analise_11_campus_mare_portais.png")
    plt.close()
    
    # Salvar dados
    for estacao_id, dados in resultados.items():
        dados['df'].to_csv(f'{OUTPUT_DIR}/analise_11_campus_mare_{estacao_id}.csv', index=False)
    print(f"✅ Dados salvos: analise_11_campus_mare_*.csv")


def analise_4_origens_bandejoes():
    """
    ANÁLISE 4: Origens para Bandejões
    Identifica as principais estações de origem das viagens que chegam
    aos bandejões (249, 250, 256) durante o pico do almoço (11h-14h).
    """
    print("\n" + "="*80)
    print("ANÁLISE 4: ORIGENS PARA BANDEJÕES NO HORÁRIO DE ALMOÇO (11h-14h)")
    print("="*80)
    
    viagens_campus = get_viagens_campus()
    
    # Viagens para bandejões no horário de almoço
    viagens_bandejao = viagens_campus.filter(
        final_station_id__in=list(ESTACOES_BANDEJAO.keys()),
        start_hour__gte=11,
        start_hour__lt=14
    )
    
    print_sql_query("Viagens para bandejões (11h-14h)", viagens_bandejao)
    
    # Top origens por bandejão
    for bandejao_id, bandejao_nome in ESTACOES_BANDEJAO.items():
        print(f"\n🍽️  {bandejao_nome} (ID {bandejao_id})")
        
        origens = viagens_bandejao.filter(
            final_station_id=bandejao_id
        ).values('initial_station_id', 'initial_station_name').annotate(
            total=Count('id')
        ).order_by('-total')[:15]
        
        print_sql_query(f"Top 15 origens para {bandejao_nome}", origens)
        
        df_origens = pd.DataFrame(list(origens))
        
        if len(df_origens) > 0:
            print(f"\n   Top 15 Origens:")
            for i, row in df_origens.iterrows():
                print(f"   {i+1:2d}. {row['initial_station_name']:40s} {row['total']:5,} viagens")
            
            # Gráfico individual
            fig, ax = plt.subplots(figsize=(14, 8))
            
            ax.barh(range(len(df_origens)), df_origens['total'], color='steelblue', alpha=0.7, edgecolor='black')
            ax.set_yticks(range(len(df_origens)))
            ax.set_yticklabels([nome[:35] for nome in df_origens['initial_station_name']], fontsize=10)
            ax.set_xlabel('Número de Viagens', fontsize=12, fontweight='bold')
            ax.set_title(f'Top 15 Origens para {bandejao_nome}\nHorário de Almoço (11h-14h)', 
                        fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)
            
            # Adicionar valores nas barras
            for i, v in enumerate(df_origens['total']):
                ax.text(v + 10, i, f'{v:,}', va='center', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(f'{OUTPUT_DIR}/analise_11_campus_bandejao_{bandejao_id}_origens.png', dpi=300, bbox_inches='tight')
            print(f"\n   ✅ Gráfico salvo: analise_11_campus_bandejao_{bandejao_id}_origens.png")
            plt.close()
            
            # Salvar dados
            df_origens.to_csv(f'{OUTPUT_DIR}/analise_11_campus_bandejao_{bandejao_id}_origens.csv', index=False)
            print(f"   ✅ Dados salvos: analise_11_campus_bandejao_{bandejao_id}_origens.csv")


def main():
    """Executa todas as análises focadas no campus."""
    print("\n" + "🚴"*40)
    print("\n   ANÁLISES FOCADAS NO CAMPUS USP")
    print("   Dataset: 59.921 viagens (origem OU destino na USP)")
    print("   Viagens internas: 34.126 (origem E destino na USP)")
    print("   Estações: 17 (IDs 242,243,245-260 exceto 244,255)")
    print("\n" + "🚴"*40)
    
    inicio = datetime.now()
    
    # Verificar se existem as viagens
    viagens_campus = get_viagens_campus()
    viagens_internas = get_viagens_internas()
    
    print(f"\n✅ Total de viagens do campus: {viagens_campus.count():,}")
    print(f"✅ Total de viagens internas: {viagens_internas.count():,}")
    
    # Executar análises
    print("\n" + "="*80)
    print("EXECUTANDO ANÁLISES...")
    print("="*80)
    
    analise_1_horarios_academicos()
    analise_2_duracao_viagens_internas()
    analise_3_mare_portais()
    analise_4_origens_bandejoes()
    
    fim = datetime.now()
    tempo_total = (fim - inicio).total_seconds()
    
    print("\n" + "="*80)
    print("✅ TODAS AS ANÁLISES CONCLUÍDAS!")
    print("="*80)
    print(f"\n⏱️  Tempo total: {tempo_total:.1f} segundos ({tempo_total/60:.1f} minutos)")
    print(f"📁 Resultados salvos em: {OUTPUT_DIR}")
    print("\n🎓 Análises prontas para inclusão na Seção 5.8 da monografia!\n")


if __name__ == '__main__':
    main()
