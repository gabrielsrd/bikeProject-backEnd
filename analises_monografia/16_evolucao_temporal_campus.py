#!/usr/bin/env python3
"""
Análise 16: Evolução Temporal das Viagens do Campus USP
Mostra a série temporal mensal com eventos marcados
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Trip
from django.db.models import Q, Count

# Definir estações USP (17 estações dentro do perímetro)
ESTACOES_USP = [
    56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 
    56713, 56640, 44878,  # 12 centrais
    37915, 48848, 38637, 56654, 42323  # 5 fronteira
]

print("=" * 80)
print("ANÁLISE 16: EVOLUÇÃO TEMPORAL DAS VIAGENS DO CAMPUS USP")
print("=" * 80)
print()

# Buscar viagens do campus
viagens_campus = Trip.objects.filter(
    Q(initial_station_id__in=ESTACOES_USP) | Q(final_station_id__in=ESTACOES_USP)
)

# Buscar todas as viagens do campus
viagens = list(viagens_campus.values('start_time'))

print(f"Total de viagens do campus: {len(viagens):,}")
print()

# Agrupar por ano-mês manualmente
from collections import Counter
viagens_por_mes = Counter()

for v in viagens:
    ano_mes = v['start_time'].strftime('%Y-%m')
    viagens_por_mes[ano_mes] += 1

# Converter para DataFrame
data = [{'ano_mes': k, 'total': v} for k, v in sorted(viagens_por_mes.items())]
df = pd.DataFrame(data)
df['data'] = pd.to_datetime(df['ano_mes'] + '-01')
df = df.sort_values('data')

print("Estatísticas mensais:")
print(f"  Mínimo: {df['total'].min():,} viagens ({df.loc[df['total'].idxmin(), 'ano_mes']})")
print(f"  Máximo: {df['total'].max():,} viagens ({df.loc[df['total'].idxmax(), 'ano_mes']})")
print(f"  Média:  {df['total'].mean():.0f} viagens/mês")
print(f"  Mediana: {df['total'].median():.0f} viagens/mês")
print()

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 6)
plt.rcParams['font.size'] = 11

# Criar figura
fig, ax = plt.subplots()

# Plot principal
ax.plot(df['data'], df['total'], 
        marker='o', linewidth=2, markersize=6,
        color='#2E86AB', label='Viagens mensais')

# Preencher área sob a curva
ax.fill_between(df['data'], 0, df['total'], alpha=0.2, color='#2E86AB')

# Marcar eventos importantes
eventos = [
    (datetime(2020, 3, 5), 'Inauguração sistema\nno campus\n(05/03/2020)', 'red', 4768),
    (datetime(2020, 3, 23), 'Lockdown\nCOVID-19\n(23/03/2020)', 'darkred', 4768),
    (datetime(2021, 9, 1), 'Retorno gradual\natividades presenciais', 'green', 3804),
]

for data, texto, cor, viagens in eventos:
    ax.axvline(x=data, color=cor, linestyle='--', linewidth=1.5, alpha=0.7, 
               label=texto.split('\n')[0])
    
    # Adicionar anotação
    ax.annotate(texto, 
                xy=(data, viagens), 
                xytext=(10, 20), 
                textcoords='offset points',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.5', facecolor=cor, alpha=0.2),
                arrowprops=dict(arrowstyle='->', color=cor, lw=1.5))

# Configurações do gráfico
ax.set_xlabel('Data', fontsize=12, fontweight='bold')
ax.set_ylabel('Número de Viagens', fontsize=12, fontweight='bold')
ax.set_title('Evolução Temporal das Viagens do Campus USP (jun/2018 - abr/2022)\n' +
             f'Total: {viagens_campus.count():,} viagens em {len(df)} meses',
             fontsize=14, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
ax.set_axisbelow(True)

# Formatar eixo Y
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Legenda
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

# Ajustar layout
plt.tight_layout()

# Salvar figura
output_path = 'analises_monografia/resultados/analise_16_evolucao_temporal_campus.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Figura salva: {output_path}")
print()

# Análise por períodos
print("Análise por períodos:")
print("-" * 60)

# Pré-pandemia (jun/2018 - fev/2020)
pre_pandemia = df[df['data'] < datetime(2020, 3, 1)]
print(f"Pré-pandemia (jun/2018 - fev/2020):")
print(f"  Meses: {len(pre_pandemia)}")
print(f"  Total viagens: {pre_pandemia['total'].sum():,}")
print(f"  Média mensal: {pre_pandemia['total'].mean():.0f}")
print()

# Inauguração + Lockdown (mar/2020 - dez/2020)
lockdown = df[(df['data'] >= datetime(2020, 3, 1)) & (df['data'] < datetime(2021, 1, 1))]
print(f"Inauguração + Lockdown (mar/2020 - dez/2020):")
print(f"  Meses: {len(lockdown)}")
print(f"  Total viagens: {lockdown['total'].sum():,}")
print(f"  Média mensal: {lockdown['total'].mean():.0f}")
print()

# Recuperação gradual (2021)
recuperacao = df[(df['data'] >= datetime(2021, 1, 1)) & (df['data'] < datetime(2022, 1, 1))]
print(f"Recuperação gradual (2021):")
print(f"  Meses: {len(recuperacao)}")
print(f"  Total viagens: {recuperacao['total'].sum():,}")
print(f"  Média mensal: {recuperacao['total'].mean():.0f}")
print()

# Consolidação (2022)
consolidacao = df[df['data'] >= datetime(2022, 1, 1)]
print(f"Consolidação (jan-abr/2022):")
print(f"  Meses: {len(consolidacao)}")
print(f"  Total viagens: {consolidacao['total'].sum():,}")
print(f"  Média mensal: {consolidacao['total'].mean():.0f}")
print()

print("=" * 80)
print("ANÁLISE CONCLUÍDA")
print("=" * 80)
