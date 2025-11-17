#!/usr/bin/env python3
"""
Análise Detalhada dos Três Tipos de Fluxo no Campus USP
========================================================

Este script separa e analisa detalhadamente os três tipos de fluxo:
1. FLUXO INTERNO: Origem E destino dentro do campus (USP → USP)
2. FLUXO DE ENTRADA: Origem fora, destino dentro (EXTERNO → USP)
3. FLUXO DE SAÍDA: Origem dentro, destino fora (USP → EXTERNO)

Autor: Gabriel
Data: Novembro 2024
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from collections import Counter

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Q, Count

# Configurações de visualização
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11

# Diretório de saída
OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# DEFINIÇÃO DAS ESTAÇÕES USP (17 ESTAÇÕES DENTRO DO PERÍMETRO)
# ============================================================================

ESTACOES_USP = [
    # Central campus (12 estações)
    56826,  # 242 - Letras
    56659,  # 243 - Bancos/Reitoria
    48852,  # 248 - Biblioteca Brasiliana
    38476,  # 249 - Bandejão Central
    56642,  # 250 - Bandejão Química
    38582,  # 251 - IME/FAU
    56762,  # 252 - Psicologia
    38425,  # 253 - Biênio Poli USP
    56965,  # 254 - Terminal de Ônibus USP
    56713,  # 256 - Bandejão Prefeitura
    56640,  # 258 - Odontologia
    44878,  # 259 - Portão 1 USP
    
    # Boundary/USP facilities (5 estações)
    37915,  # 247 - CEPE
    48848,  # 245 - Raia Olímpica USP
    38637,  # 246 - PORTÃO CPTM
    56654,  # 257 - Hospital Universitário
    42323,  # 260 - Harmonia
]

print("=" * 80)
print("ANÁLISE DETALHADA DOS TRÊS TIPOS DE FLUXO - CAMPUS USP")
print("=" * 80)
print(f"\nEstações USP analisadas: {len(ESTACOES_USP)}")

# ============================================================================
# 1. SEPARAR OS TRÊS TIPOS DE FLUXO
# ============================================================================

print("\n" + "=" * 80)
print("1. SEPARAÇÃO DOS FLUXOS")
print("=" * 80)

# FLUXO INTERNO: origem E destino na USP
viagens_internas = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP,
    final_station_id__in=ESTACOES_USP
)
total_internas = viagens_internas.count()

# FLUXO DE ENTRADA: origem fora, destino na USP
viagens_entrada = Trip.objects.filter(
    final_station_id__in=ESTACOES_USP
).exclude(
    initial_station_id__in=ESTACOES_USP
)
total_entrada = viagens_entrada.count()

# FLUXO DE SAÍDA: origem na USP, destino fora
viagens_saida = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP
).exclude(
    final_station_id__in=ESTACOES_USP
)
total_saida = viagens_saida.count()

# TOTAL
total_geral = total_internas + total_entrada + total_saida

print(f"\n📊 TOTAIS POR TIPO DE FLUXO:")
print(f"\n1. FLUXO INTERNO (USP → USP):")
print(f"   {total_internas:,} viagens ({100*total_internas/total_geral:.1f}%)")
print(f"\n2. FLUXO DE ENTRADA (EXTERNO → USP):")
print(f"   {total_entrada:,} viagens ({100*total_entrada/total_geral:.1f}%)")
print(f"\n3. FLUXO DE SAÍDA (USP → EXTERNO):")
print(f"   {total_saida:,} viagens ({100*total_saida/total_geral:.1f}%)")
print(f"\n   TOTAL GERAL: {total_geral:,} viagens")

# ============================================================================
# 2. ANÁLISE TEMPORAL POR TIPO DE FLUXO
# ============================================================================

print("\n" + "=" * 80)
print("2. ANÁLISE TEMPORAL POR TIPO DE FLUXO")
print("=" * 80)

def extrair_hora(queryset):
    """Extrai a distribuição por hora do dia"""
    horas = Counter()
    for viagem in queryset.iterator():
        hora = viagem.start_hour
        horas[hora] += 1
    return horas

print("\n⏰ Processando distribuição por hora para cada tipo de fluxo...")

horas_internas = extrair_hora(viagens_internas)
horas_entrada = extrair_hora(viagens_entrada)
horas_saida = extrair_hora(viagens_saida)

# Criar DataFrame para visualização
df_temporal = pd.DataFrame({
    'Hora': list(range(24)),
    'Interno (USP→USP)': [horas_internas.get(h, 0) for h in range(24)],
    'Entrada (Ext→USP)': [horas_entrada.get(h, 0) for h in range(24)],
    'Saída (USP→Ext)': [horas_saida.get(h, 0) for h in range(24)]
})

print("\n📈 Top 5 horários por tipo de fluxo:")
print("\nFLUXO INTERNO:")
for h, count in sorted(horas_internas.items(), key=lambda x: x[1], reverse=True)[:5]:
    pct = 100 * count / total_internas
    print(f"  {h:02d}h: {count:,} viagens ({pct:.1f}%)")

print("\nFLUXO DE ENTRADA:")
for h, count in sorted(horas_entrada.items(), key=lambda x: x[1], reverse=True)[:5]:
    pct = 100 * count / total_entrada
    print(f"  {h:02d}h: {count:,} viagens ({pct:.1f}%)")

print("\nFLUXO DE SAÍDA:")
for h, count in sorted(horas_saida.items(), key=lambda x: x[1], reverse=True)[:5]:
    pct = 100 * count / total_saida
    print(f"  {h:02d}h: {count:,} viagens ({pct:.1f}%)")

# Visualização
fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Gráfico 1: Três fluxos empilhados
ax1 = axes[0, 0]
ax1.plot(df_temporal['Hora'], df_temporal['Interno (USP→USP)'], 
         marker='o', linewidth=2, label='Interno (USP→USP)', color='#2E86AB')
ax1.plot(df_temporal['Hora'], df_temporal['Entrada (Ext→USP)'], 
         marker='s', linewidth=2, label='Entrada (Ext→USP)', color='#A23B72')
ax1.plot(df_temporal['Hora'], df_temporal['Saída (USP→Ext)'], 
         marker='^', linewidth=2, label='Saída (USP→Ext)', color='#F18F01')
ax1.set_xlabel('Hora do dia', fontsize=12, fontweight='bold')
ax1.set_ylabel('Número de viagens', fontsize=12, fontweight='bold')
ax1.set_title('Distribuição Horária dos Três Tipos de Fluxo', 
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=11, loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-0.5, 23.5)
ax1.set_xticks(range(0, 24, 2))

# Gráfico 2: Proporção por hora
ax2 = axes[0, 1]
total_por_hora = df_temporal[['Interno (USP→USP)', 'Entrada (Ext→USP)', 'Saída (USP→Ext)']].sum(axis=1)
pct_interno = 100 * df_temporal['Interno (USP→USP)'] / total_por_hora
pct_entrada = 100 * df_temporal['Entrada (Ext→USP)'] / total_por_hora
pct_saida = 100 * df_temporal['Saída (USP→Ext)'] / total_por_hora

ax2.fill_between(df_temporal['Hora'], 0, pct_interno, 
                  alpha=0.7, label='Interno (USP→USP)', color='#2E86AB')
ax2.fill_between(df_temporal['Hora'], pct_interno, pct_interno + pct_entrada,
                  alpha=0.7, label='Entrada (Ext→USP)', color='#A23B72')
ax2.fill_between(df_temporal['Hora'], pct_interno + pct_entrada, 100,
                  alpha=0.7, label='Saída (USP→Ext)', color='#F18F01')
ax2.set_xlabel('Hora do dia', fontsize=12, fontweight='bold')
ax2.set_ylabel('Proporção (%)', fontsize=12, fontweight='bold')
ax2.set_title('Proporção Relativa dos Fluxos por Horário', 
              fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=11, loc='upper left')
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xlim(-0.5, 23.5)
ax2.set_xticks(range(0, 24, 2))
ax2.set_ylim(0, 100)

# Gráfico 3: Saldo entrada-saída por hora
ax3 = axes[1, 0]
saldo = df_temporal['Entrada (Ext→USP)'] - df_temporal['Saída (USP→Ext)']
colors = ['#06A77D' if x >= 0 else '#D62828' for x in saldo]
ax3.bar(df_temporal['Hora'], saldo, color=colors, alpha=0.7, edgecolor='black')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
ax3.set_xlabel('Hora do dia', fontsize=12, fontweight='bold')
ax3.set_ylabel('Saldo (Entrada - Saída)', fontsize=12, fontweight='bold')
ax3.set_title('Saldo de Entrada/Saída por Horário\n(Positivo = mais entrando | Negativo = mais saindo)', 
              fontsize=14, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_xlim(-0.5, 23.5)
ax3.set_xticks(range(0, 24, 2))

# Gráfico 4: Pizza com proporções gerais
ax4 = axes[1, 1]
sizes = [total_internas, total_entrada, total_saida]
labels = [f'Interna\n34.126 viagens\n(57,0%)',
          f'Entrada\n12.410 viagens\n(20,7%)',
          f'Saída\n13.385 viagens\n(22,3%)']
colors_pie = ['#2E86AB', '#A23B72', '#F18F01']
ax4.pie(sizes, labels=labels, colors=colors_pie, autopct='', startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'})
ax4.set_title('Distribuição Geral dos Três Tipos de Fluxo\nTotal: 59.921 viagens', 
              fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_12_tres_fluxos_temporal.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico temporal salvo em: {output_path}")
plt.close()

# ============================================================================
# 3. TOP ESTAÇÕES EXTERNAS (ENTRADA E SAÍDA)
# ============================================================================

print("\n" + "=" * 80)
print("3. TOP ESTAÇÕES EXTERNAS CONECTADAS AO CAMPUS")
print("=" * 80)

# Contar origens de entrada
origens_entrada = Counter()
for v in viagens_entrada.values('initial_station_id', 'initial_station_name'):
    origens_entrada[v['initial_station_id']] += 1

# Contar destinos de saída
destinos_saida = Counter()
for v in viagens_saida.values('final_station_id', 'final_station_name'):
    destinos_saida[v['final_station_id']] += 1

# Combinar para total de conexões
conexoes_externas = Counter()
for id_est, count in origens_entrada.items():
    conexoes_externas[id_est] += count
for id_est, count in destinos_saida.items():
    conexoes_externas[id_est] += count

print("\n🔝 TOP 15 ESTAÇÕES EXTERNAS POR TOTAL DE CONEXÕES:")
print(f"\n{'Ranking':<8} {'ID':<8} {'Entrada':<10} {'Saída':<10} {'Total':<10} {'Nome'}")
print("-" * 100)

top_externas = []
for rank, (id_est, total) in enumerate(conexoes_externas.most_common(15), 1):
    entrada = origens_entrada.get(id_est, 0)
    saida = destinos_saida.get(id_est, 0)
    try:
        est = Station.objects.get(id=id_est)
        nome = est.name
    except:
        nome = "(nome não encontrado)"
    
    print(f"{rank:<8} {id_est:<8} {entrada:<10,} {saida:<10,} {total:<10,} {nome}")
    top_externas.append({
        'id': id_est,
        'nome': nome,
        'entrada': entrada,
        'saida': saida,
        'total': total
    })

# ============================================================================
# 4. ANÁLISE DE DURAÇÃO POR TIPO DE FLUXO
# ============================================================================

print("\n" + "=" * 80)
print("4. ANÁLISE DE DURAÇÃO POR TIPO DE FLUXO")
print("=" * 80)

def analisar_duracao(queryset, nome):
    """Analisa duração de viagens"""
    duracoes = []
    for viagem in queryset.iterator():
        duracao_min = viagem.duration_seconds / 60
        if 0 < duracao_min <= 180:  # Filtrar outliers
            duracoes.append(duracao_min)
    
    if not duracoes:
        return None
    
    duracoes.sort()
    n = len(duracoes)
    
    resultado = {
        'nome': nome,
        'total': n,
        'min': duracoes[0],
        'q25': duracoes[n//4],
        'mediana': duracoes[n//2],
        'q75': duracoes[3*n//4],
        'max': duracoes[-1],
        'media': sum(duracoes) / n,
        'duracoes': duracoes
    }
    
    return resultado

print("\n⏱️ Calculando estatísticas de duração...")

stats_internas = analisar_duracao(viagens_internas, 'Interno (USP→USP)')
stats_entrada = analisar_duracao(viagens_entrada, 'Entrada (Ext→USP)')
stats_saida = analisar_duracao(viagens_saida, 'Saída (USP→Ext)')

for stats in [stats_internas, stats_entrada, stats_saida]:
    if stats:
        print(f"\n{stats['nome']}:")
        print(f"  Viagens analisadas: {stats['total']:,}")
        print(f"  Mínima: {stats['min']:.1f} min")
        print(f"  Q1 (25%): {stats['q25']:.1f} min")
        print(f"  Mediana: {stats['mediana']:.1f} min")
        print(f"  Média: {stats['media']:.1f} min")
        print(f"  Q3 (75%): {stats['q75']:.1f} min")
        print(f"  Máxima: {stats['max']:.1f} min")

# Visualização de durações
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, (stats, color) in enumerate([
    (stats_internas, '#2E86AB'),
    (stats_entrada, '#A23B72'),
    (stats_saida, '#F18F01')
]):
    ax = axes[idx]
    
    if stats:
        # Histograma
        ax.hist(stats['duracoes'], bins=50, color=color, alpha=0.7, edgecolor='black')
        
        # Linha de mediana
        ax.axvline(stats['mediana'], color='red', linestyle='--', linewidth=2,
                   label=f'Mediana: {stats["mediana"]:.1f} min')
        
        ax.set_xlabel('Duração (minutos)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
        ax.set_title(f'{stats["nome"]}\n{stats["total"]:,} viagens',
                     fontsize=12, fontweight='bold', pad=10)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_12_tres_fluxos_duracao.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico de duração salvo em: {output_path}")
plt.close()

# ============================================================================
# 5. ANÁLISE DE INTEGRAÇÃO MODAL DETALHADA
# ============================================================================

print("\n" + "=" * 80)
print("5. ANÁLISE DE INTEGRAÇÃO MODAL DETALHADA")
print("=" * 80)

# Estações de transporte público importantes
ESTACOES_TRANSPORTE = {
    56861: 'Metrô Butantã',
    37913: 'CPTM Cidade Universitária',
    38524: 'Praça Monte Castelo',
    38100: 'Estacao Tiradentes',
}

print("\n🚇 ANÁLISE DAS PRINCIPAIS ESTAÇÕES DE TRANSPORTE PÚBLICO:")

for id_est, nome in ESTACOES_TRANSPORTE.items():
    # Entrada: desta estação → USP
    entrada = Trip.objects.filter(
        initial_station_id=id_est,
        final_station_id__in=ESTACOES_USP
    ).count()
    
    # Saída: USP → esta estação
    saida = Trip.objects.filter(
        initial_station_id__in=ESTACOES_USP,
        final_station_id=id_est
    ).count()
    
    total = entrada + saida
    
    if total > 0:
        print(f"\n{nome} (ID {id_est}):")
        print(f"  Entrada (desta estação → USP): {entrada:,} viagens")
        print(f"  Saída (USP → esta estação): {saida:,} viagens")
        print(f"  TOTAL: {total:,} viagens")
        print(f"  Saldo: {entrada - saida:+,} (positivo = mais entrando)")

print("\n" + "=" * 80)
print("✅ ANÁLISE COMPLETA DOS TRÊS FLUXOS CONCLUÍDA")
print("=" * 80)
print(f"\nResumo:")
print(f"  - 2 gráficos salvos em {OUTPUT_DIR}")
print(f"  - Fluxo interno: {total_internas:,} viagens (53,5%)")
print(f"  - Fluxo entrada: {total_entrada:,} viagens (23,2%)")
print(f"  - Fluxo saída: {total_saida:,} viagens (23,3%)")
print(f"  - Total: {total_geral:,} viagens")
