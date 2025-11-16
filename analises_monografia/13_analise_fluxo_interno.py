#!/usr/bin/env python3
"""
Análise Específica: FLUXO INTERNO (USP → USP)
==============================================

Análise detalhada das viagens que começam E terminam dentro do campus USP.
Foco em padrões de circulação interna, rotas mais usadas, e comportamento
específico do transporte intra-campus.

Autor: Gabriel
Data: Novembro 2024
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter, defaultdict

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Q

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estações USP
ESTACOES_USP = [56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323]

print("=" * 80)
print("ANÁLISE ESPECÍFICA: FLUXO INTERNO (USP → USP)")
print("=" * 80)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

print("\n📊 Carregando viagens internas...")
viagens_internas = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP,
    final_station_id__in=ESTACOES_USP
)
total = viagens_internas.count()
print(f"   Total: {total:,} viagens")

# Criar mapeamento de IDs para nomes
estacoes_map = {}
for est_id in ESTACOES_USP:
    try:
        est = Station.objects.get(id=est_id)
        estacoes_map[est_id] = est.name
    except:
        estacoes_map[est_id] = f"Estação {est_id}"

# ============================================================================
# 2. TOP 20 ROTAS MAIS POPULARES
# ============================================================================

print("\n" + "=" * 80)
print("1. TOP 20 ROTAS INTERNAS MAIS POPULARES")
print("=" * 80)

rotas = Counter()
for v in viagens_internas.values('initial_station_id', 'final_station_id'):
    origem = v['initial_station_id']
    destino = v['final_station_id']
    rotas[(origem, destino)] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'Origem → Destino'}")
print("-" * 80)

top_rotas = []
for rank, ((origem_id, destino_id), count) in enumerate(rotas.most_common(20), 1):
    pct = 100 * count / total
    origem_nome = estacoes_map.get(origem_id, str(origem_id))
    destino_nome = estacoes_map.get(destino_id, str(destino_id))
    print(f"{rank:<4} {count:<10,} {origem_nome} → {destino_nome}")
    top_rotas.append({
        'rank': rank,
        'origem_id': origem_id,
        'destino_id': destino_id,
        'origem': origem_nome,
        'destino': destino_nome,
        'viagens': count,
        'pct': pct
    })

# ============================================================================
# 3. ESTAÇÕES MAIS ATIVAS (ORIGEM E DESTINO)
# ============================================================================

print("\n" + "=" * 80)
print("2. ESTAÇÕES MAIS ATIVAS COMO ORIGEM E DESTINO")
print("=" * 80)

origens = Counter()
destinos = Counter()

for v in viagens_internas.values('initial_station_id', 'final_station_id'):
    origens[v['initial_station_id']] += 1
    destinos[v['final_station_id']] += 1

print("\n📍 TOP 10 ORIGENS:")
print(f"{'#':<4} {'Viagens':<10} {'Estação'}")
print("-" * 60)
for rank, (est_id, count) in enumerate(origens.most_common(10), 1):
    pct = 100 * count / total
    print(f"{rank:<4} {count:<10,} ({pct:5.1f}%)  {estacoes_map.get(est_id, str(est_id))}")

print("\n🎯 TOP 10 DESTINOS:")
print(f"{'#':<4} {'Viagens':<10} {'Estação'}")
print("-" * 60)
for rank, (est_id, count) in enumerate(destinos.most_common(10), 1):
    pct = 100 * count / total
    print(f"{rank:<4} {count:<10,} ({pct:5.1f}%)  {estacoes_map.get(est_id, str(est_id))}")

# ============================================================================
# 4. ANÁLISE DE VIAGENS CIRCULARES (mesma origem e destino)
# ============================================================================

print("\n" + "=" * 80)
print("3. VIAGENS CIRCULARES (mesma estação origem/destino)")
print("=" * 80)

circulares_count = {}
for v in viagens_internas.values('initial_station_id', 'final_station_id'):
    if v['initial_station_id'] == v['final_station_id']:
        est_id = v['initial_station_id']
        circulares_count[est_id] = circulares_count.get(est_id, 0) + 1

total_circulares = sum(circulares_count.values())
pct_circulares = 100 * total_circulares / total

print(f"\n✓ Total de viagens circulares: {total_circulares:,} ({pct_circulares:.1f}%)")
print(f"\n{'#':<4} {'Viagens':<10} {'Estação'}")
print("-" * 60)

circulares_sorted = sorted(circulares_count.items(), key=lambda x: x[1], reverse=True)
for rank, (est_id, count) in enumerate(circulares_sorted[:10], 1):
    pct = 100 * count / total_circulares
    print(f"{rank:<4} {count:<10,} ({pct:5.1f}%)  {estacoes_map.get(est_id, str(est_id))}")

# ============================================================================
# 5. DISTRIBUIÇÃO TEMPORAL
# ============================================================================

print("\n" + "=" * 80)
print("4. DISTRIBUIÇÃO TEMPORAL DAS VIAGENS INTERNAS")
print("=" * 80)

horas = Counter()
dias = Counter()

for v in viagens_internas.iterator():
    horas[v.start_hour] += 1
    dias[v.start_day] += 1

print("\n⏰ DISTRIBUIÇÃO POR HORA:")
print(f"{'Hora':<6} {'Viagens':<10} {'%':<8} {'Barra'}")
print("-" * 60)

for hora in range(24):
    count = horas.get(hora, 0)
    pct = 100 * count / total
    barra = '█' * int(pct * 2)
    print(f"{hora:02d}h   {count:<10,} {pct:6.2f}%  {barra}")

print("\n📅 DISTRIBUIÇÃO POR DIA DA SEMANA:")
dias_nome = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
print(f"{'Dia':<12} {'Viagens':<10} {'%':<8} {'Barra'}")
print("-" * 60)

for dia_num in range(7):
    count = dias.get(dia_num, 0)
    pct = 100 * count / total if total > 0 else 0
    barra = '█' * int(pct / 2)
    print(f"{dias_nome[dia_num]:<12} {count:<10,} {pct:6.2f}%  {barra}")

# ============================================================================
# 6. VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 80)
print("5. GERANDO VISUALIZAÇÕES")
print("=" * 80)

# Gráfico 1: Top 15 rotas
fig, axes = plt.subplots(2, 2, figsize=(18, 14))

ax1 = axes[0, 0]
top15_rotas = top_rotas[:15]
labels = [f"{r['origem'].split('-')[0].strip()[:15]} →\n{r['destino'].split('-')[0].strip()[:15]}" 
          for r in top15_rotas]
viagens = [r['viagens'] for r in top15_rotas]
colors = sns.color_palette("viridis", len(top15_rotas))

ax1.barh(range(len(top15_rotas)), viagens, color=colors, edgecolor='black')
ax1.set_yticks(range(len(top15_rotas)))
ax1.set_yticklabels(labels, fontsize=9)
ax1.set_xlabel('Número de viagens', fontsize=11, fontweight='bold')
ax1.set_title('Top 15 Rotas Internas Mais Populares', fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(True, alpha=0.3, axis='x')

# Adicionar valores nas barras
for i, v in enumerate(viagens):
    ax1.text(v + 50, i, f'{v:,}', va='center', fontsize=9)

# Gráfico 2: Top 10 Origens vs Destinos
ax2 = axes[0, 1]
top10_ids = [est_id for est_id, _ in origens.most_common(10)]
nomes = [estacoes_map.get(est_id, str(est_id)).split('-')[0].strip()[:20] for est_id in top10_ids]
origem_vals = [origens[est_id] for est_id in top10_ids]
destino_vals = [destinos[est_id] for est_id in top10_ids]

x = range(len(top10_ids))
width = 0.35
ax2.bar([i - width/2 for i in x], origem_vals, width, label='Como Origem', 
        color='#2E86AB', edgecolor='black')
ax2.bar([i + width/2 for i in x], destino_vals, width, label='Como Destino', 
        color='#A23B72', edgecolor='black')

ax2.set_xlabel('Estação', fontsize=11, fontweight='bold')
ax2.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Estações: Origem vs Destino', fontsize=13, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(nomes, rotation=45, ha='right', fontsize=9)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# Gráfico 3: Distribuição por hora
ax3 = axes[1, 0]
horas_list = list(range(24))
viagens_por_hora = [horas.get(h, 0) for h in horas_list]
colors_hora = ['#06A77D' if h in [7, 11, 12, 16, 17, 18] else '#1E88E5' for h in horas_list]

ax3.bar(horas_list, viagens_por_hora, color=colors_hora, edgecolor='black', alpha=0.8)
ax3.set_xlabel('Hora do dia', fontsize=11, fontweight='bold')
ax3.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax3.set_title('Distribuição Horária - Fluxo Interno\n(Destaque: horários acadêmicos)', 
              fontsize=13, fontweight='bold', pad=15)
ax3.set_xticks(range(0, 24, 2))
ax3.grid(True, alpha=0.3, axis='y')

# Adicionar anotações nos picos
picos = [(11, horas[11]), (17, horas[17]), (12, horas[12])]
for hora, valor in picos:
    ax3.annotate(f'{valor:,}', xy=(hora, valor), xytext=(hora, valor + 200),
                ha='center', fontsize=9, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

# Gráfico 4: Proporção de viagens circulares
ax4 = axes[1, 1]
sizes = [total_circulares, total - total_circulares]
labels_pie = [f'Circulares\n(mesma estação)\n{total_circulares:,}\n({pct_circulares:.1f}%)',
              f'Diferentes estações\n{total - total_circulares:,}\n({100-pct_circulares:.1f}%)']
colors_pie = ['#F18F01', '#2E86AB']
explode = (0.05, 0)

ax4.pie(sizes, explode=explode, labels=labels_pie, colors=colors_pie, autopct='',
        startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax4.set_title('Proporção de Viagens Circulares', fontsize=13, fontweight='bold', pad=15)

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_13_fluxo_interno.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# 7. ESTATÍSTICAS FINAIS
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO - FLUXO INTERNO (USP → USP)")
print("=" * 80)

print(f"""
Total de viagens internas: {total:,}

Top 3 Rotas:
  1. {top_rotas[0]['origem']} → {top_rotas[0]['destino']}: {top_rotas[0]['viagens']:,} viagens
  2. {top_rotas[1]['origem']} → {top_rotas[1]['destino']}: {top_rotas[1]['viagens']:,} viagens
  3. {top_rotas[2]['origem']} → {top_rotas[2]['destino']}: {top_rotas[2]['viagens']:,} viagens

Viagens circulares: {total_circulares:,} ({pct_circulares:.1f}%)

Picos horários:
  - 17h: {horas[17]:,} viagens
  - 11h: {horas[11]:,} viagens
  - 12h: {horas[12]:,} viagens

Estação mais ativa (origem): {estacoes_map[origens.most_common(1)[0][0]]} ({origens.most_common(1)[0][1]:,} partidas)
Estação mais ativa (destino): {estacoes_map[destinos.most_common(1)[0][0]]} ({destinos.most_common(1)[0][1]:,} chegadas)
""")

print("=" * 80)
print("✅ ANÁLISE CONCLUÍDA")
print("=" * 80)
