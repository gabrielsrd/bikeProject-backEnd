#!/usr/bin/env python3
"""
Gráfico Detalhado: Viagens Circulares por Estação - Campus USP
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Trip, Station

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estações USP
ESTACOES_USP = [56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 
                56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323]

print("=" * 80)
print("GERANDO GRÁFICO: VIAGENS CIRCULARES POR ESTAÇÃO")
print("=" * 80)

# Buscar viagens circulares
viagens_circulares = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP
).filter(
    initial_station_id=django.db.models.F('final_station_id')
)

# Contar por estação
estacoes_count = Counter()
for v in viagens_circulares.values('initial_station_id'):
    estacoes_count[v['initial_station_id']] += 1

total_circulares = sum(estacoes_count.values())

# Criar lista com todas as 17 estações
dados_estacoes = []
for est_id in ESTACOES_USP:
    count = estacoes_count.get(est_id, 0)
    try:
        est = Station.objects.get(id=est_id)
        nome = est.name.split('-')[-1].strip() if '-' in est.name else est.name
    except:
        nome = f"Est. {est_id}"
    
    # Calcular duração média
    viagens_est = Trip.objects.filter(
        initial_station_id=est_id,
        final_station_id=est_id
    )
    
    duracoes = []
    for v in viagens_est.iterator():
        duracao_min = v.duration_seconds / 60
        if 0 < duracao_min < 180:
            duracoes.append(duracao_min)
    
    duracao_media = sum(duracoes) / len(duracoes) if duracoes else 0
    
    dados_estacoes.append({
        'id': est_id,
        'nome': nome,
        'viagens': count,
        'pct': 100 * count / total_circulares if total_circulares > 0 else 0,
        'duracao_media': duracao_media
    })

# Ordenar por viagens
dados_estacoes.sort(key=lambda x: x['viagens'], reverse=True)

print(f"\nTotal de viagens circulares: {total_circulares:,}")
print(f"Gerando gráficos...\n")

# ============================================================================
# CRIAR GRÁFICO
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Gráfico 1: Todas as 17 estações (barras horizontais)
ax1 = axes[0, 0]
nomes = [d['nome'][:25] for d in dados_estacoes]
viagens = [d['viagens'] for d in dados_estacoes]

# Cores: destaque para Bandejão
colors = ['#E63946' if d['nome'] == 'Bandejão Central' else '#457B9D' 
          for d in dados_estacoes]

bars = ax1.barh(range(len(nomes)), viagens, color=colors, edgecolor='black', alpha=0.8)
ax1.set_yticks(range(len(nomes)))
ax1.set_yticklabels(nomes, fontsize=9)
ax1.set_xlabel('Número de viagens circulares', fontsize=11, fontweight='bold')
ax1.set_title('Viagens Circulares por Estação - Campus USP\n(Total: {:,} viagens)'.format(total_circulares), 
              fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(True, alpha=0.3, axis='x')

# Adicionar valores nas barras
for i, (bar, v) in enumerate(zip(bars, viagens)):
    if v > 0:
        ax1.text(v + 50, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 2: Top 10 com percentuais
ax2 = axes[0, 1]
top10 = dados_estacoes[:10]
nomes_top10 = [d['nome'][:25] for d in top10]
viagens_top10 = [d['viagens'] for d in top10]
pcts_top10 = [d['pct'] for d in top10]

colors_top10 = sns.color_palette("rocket", len(nomes_top10))
bars2 = ax2.barh(range(len(nomes_top10)), viagens_top10, 
                 color=colors_top10, edgecolor='black', alpha=0.8)
ax2.set_yticks(range(len(nomes_top10)))
ax2.set_yticklabels(nomes_top10, fontsize=9)
ax2.set_xlabel('Número de viagens circulares', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Estações com Mais Viagens Circulares', 
              fontsize=13, fontweight='bold', pad=15)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

# Adicionar valores e %
for i, (bar, v, pct) in enumerate(zip(bars2, viagens_top10, pcts_top10)):
    ax2.text(v + 50, i, f'{v:,} ({pct:.1f}%)', va='center', fontsize=8)

# Gráfico 3: Pizza - Bandejão vs Outras
ax3 = axes[1, 0]
bandejao_viagens = dados_estacoes[0]['viagens']  # Bandejão é o primeiro (maior)
outras_viagens = total_circulares - bandejao_viagens

sizes = [bandejao_viagens, outras_viagens]
labels = [f'Bandejão Central\n{bandejao_viagens:,} viagens\n({100*bandejao_viagens/total_circulares:.1f}%)',
          f'Outras 16 Estações\n{outras_viagens:,} viagens\n({100*outras_viagens/total_circulares:.1f}%)']
colors_pie = ['#E63946', '#457B9D']
explode = (0.1, 0)

ax3.pie(sizes, explode=explode, labels=labels, colors=colors_pie, autopct='',
        startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title('Concentração no Bandejão Central', 
              fontsize=13, fontweight='bold', pad=15)

# Gráfico 4: Duração média por estação (top 10)
ax4 = axes[1, 1]
nomes_dur = [d['nome'][:25] for d in top10]
duracoes = [d['duracao_media'] for d in top10]

colors_dur = sns.color_palette("viridis", len(nomes_dur))
bars4 = ax4.barh(range(len(nomes_dur)), duracoes, 
                 color=colors_dur, edgecolor='black', alpha=0.8)
ax4.set_yticks(range(len(nomes_dur)))
ax4.set_yticklabels(nomes_dur, fontsize=9)
ax4.set_xlabel('Duração média (minutos)', fontsize=11, fontweight='bold')
ax4.set_title('Duração Média das Viagens Circulares\n(Top 10 estações)', 
              fontsize=13, fontweight='bold', pad=15)
ax4.invert_yaxis()
ax4.grid(True, alpha=0.3, axis='x')

# Adicionar valores
for i, (bar, dur) in enumerate(zip(bars4, duracoes)):
    if dur > 0:
        ax4.text(dur + 1, i, f'{dur:.1f} min', va='center', fontsize=8)

# Linha de referência (duração média geral)
duracao_media_geral = sum(d['duracao_media'] * d['viagens'] for d in top10) / sum(d['viagens'] for d in top10)
ax4.axvline(duracao_media_geral, color='red', linestyle='--', linewidth=2,
           label=f'Média geral: {duracao_media_geral:.1f} min')
ax4.legend(fontsize=10)

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'viagens_circulares_por_estacao.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# TABELA RESUMO
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO - VIAGENS CIRCULARES POR ESTAÇÃO")
print("=" * 80)

print(f"\n{'#':<4} {'Estação':<30} {'Viagens':<10} {'%':<8} {'Duração Média'}")
print("-" * 80)

for rank, d in enumerate(dados_estacoes, 1):
    print(f"{rank:<4} {d['nome'][:28]:<30} {d['viagens']:<10,} {d['pct']:6.2f}%  {d['duracao_media']:6.1f} min")

print("\n" + "=" * 80)
print(f"TOTAL: {total_circulares:,} viagens circulares")
print(f"Bandejão Central: {bandejao_viagens:,} ({100*bandejao_viagens/total_circulares:.1f}%)")
print(f"Outras 16 estações: {outras_viagens:,} ({100*outras_viagens/total_circulares:.1f}%)")
print("=" * 80)
