#!/usr/bin/env python3
"""
Análise Específica: FLUXO DE SAÍDA (USP → EXTERNO)
===================================================

Análise detalhada das viagens que começam DENTRO do campus e terminam FORA.
Foco em padrões de saída do campus, principais destinos externos,
e comportamento de integração modal (primeira milha de saída).

Autor: Gabriel
Data: Novembro 2024
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

from ciclovias.models import Station, Trip

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estações USP
ESTACOES_USP = [56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323]

print("=" * 80)
print("ANÁLISE ESPECÍFICA: FLUXO DE SAÍDA (USP → EXTERNO)")
print("=" * 80)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

print("\n📊 Carregando viagens de saída...")
viagens_saida = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP
).exclude(
    final_station_id__in=ESTACOES_USP
)
total = viagens_saida.count()
print(f"   Total: {total:,} viagens")

# Criar mapeamento de estações USP
estacoes_usp_map = {}
for est_id in ESTACOES_USP:
    try:
        est = Station.objects.get(id=est_id)
        estacoes_usp_map[est_id] = est.name
    except:
        estacoes_usp_map[est_id] = f"Estação {est_id}"

# ============================================================================
# 2. TOP 15 ORIGENS NO CAMPUS (De onde saem do campus)
# ============================================================================

print("\n" + "=" * 80)
print("1. TOP 15 ORIGENS NO CAMPUS (De onde saem)")
print("=" * 80)

origens_campus = Counter()
for v in viagens_saida.values('initial_station_id'):
    origens_campus[v['initial_station_id']] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Origem no Campus'}")
print("-" * 80)

top_origens = []
for rank, (est_id, count) in enumerate(origens_campus.most_common(15), 1):
    pct = 100 * count / total
    nome = estacoes_usp_map.get(est_id, f"Estação {est_id}")
    print(f"{rank:<4} {count:<10,} {pct:6.2f}%  {nome}")
    top_origens.append({
        'rank': rank,
        'id': est_id,
        'nome': nome,
        'viagens': count,
        'pct': pct
    })

# ============================================================================
# 3. TOP 20 DESTINOS EXTERNOS (Para onde vão)
# ============================================================================

print("\n" + "=" * 80)
print("2. TOP 20 DESTINOS EXTERNOS (Para onde vão do campus)")
print("=" * 80)

destinos_externos = Counter()
for v in viagens_saida.values('final_station_id', 'final_station_name'):
    destinos_externos[v['final_station_id']] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Destino Externo'}")
print("-" * 80)

top_destinos = []
for rank, (est_id, count) in enumerate(destinos_externos.most_common(20), 1):
    pct = 100 * count / total
    try:
        est = Station.objects.get(id=est_id)
        nome = est.name
    except:
        # Buscar do primeiro registro com esse ID
        v = viagens_saida.filter(final_station_id=est_id).first()
        nome = v.final_station_name if v else f"Estação {est_id}"
    
    print(f"{rank:<4} {count:<10,} {pct:6.2f}%  {nome}")
    top_destinos.append({
        'rank': rank,
        'id': est_id,
        'nome': nome,
        'viagens': count,
        'pct': pct
    })

# ============================================================================
# 4. TOP 15 PARES ORIGEM-DESTINO (rotas de saída mais usadas)
# ============================================================================

print("\n" + "=" * 80)
print("3. TOP 15 ROTAS DE SAÍDA MAIS USADAS")
print("=" * 80)

rotas_saida = Counter()
for v in viagens_saida.values('initial_station_id', 'final_station_id', 'final_station_name'):
    origem_id = v['initial_station_id']
    destino_id = v['final_station_id']
    rotas_saida[(origem_id, destino_id)] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'Rota (Origem Campus → Destino Externo)'}")
print("-" * 100)

top_rotas = []
for rank, ((origem_id, destino_id), count) in enumerate(rotas_saida.most_common(15), 1):
    pct = 100 * count / total
    
    origem_nome = estacoes_usp_map.get(origem_id, f"Estação {origem_id}")
    
    # Nome destino
    try:
        destino_est = Station.objects.get(id=destino_id)
        destino_nome = destino_est.name
    except:
        v = viagens_saida.filter(final_station_id=destino_id).first()
        destino_nome = v.final_station_name if v else f"Estação {destino_id}"
    
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
# 5. ANÁLISE TEMPORAL
# ============================================================================

print("\n" + "=" * 80)
print("4. DISTRIBUIÇÃO TEMPORAL DO FLUXO DE SAÍDA")
print("=" * 80)

horas = Counter()
dias = Counter()

for v in viagens_saida.iterator():
    horas[v.start_hour] += 1
    dias[v.start_day] += 1

print("\n⏰ DISTRIBUIÇÃO POR HORA (Quando as pessoas SAEM do campus):")
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
# 6. IDENTIFICAR DESTINOS DE TRANSPORTE PÚBLICO
# ============================================================================

print("\n" + "=" * 80)
print("5. DESTINOS DE TRANSPORTE PÚBLICO (Metrô, CPTM, Trem)")
print("=" * 80)

# Palavras-chave para identificar transporte público
palavras_tp = ['metrô', 'metro', 'cptm', 'trem', 'estacao', 'estação']

destinos_tp = []
total_tp = 0

for destino in top_destinos:
    nome_lower = destino['nome'].lower()
    if any(palavra in nome_lower for palavra in palavras_tp):
        destinos_tp.append(destino)
        total_tp += destino['viagens']

pct_tp = 100 * total_tp / total

print(f"\n✓ Viagens para estações de transporte público: {total_tp:,} ({pct_tp:.1f}%)")
print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Estação de Transporte'}")
print("-" * 80)

for i, destino in enumerate(destinos_tp[:10], 1):
    print(f"{i:<4} {destino['viagens']:<10,} {destino['pct']:6.2f}%  {destino['nome']}")

# ============================================================================
# 7. COMPARAÇÃO ORIGENS NO CAMPUS
# ============================================================================

print("\n" + "=" * 80)
print("6. ESTAÇÕES-PORTAL vs ESTAÇÕES INTERNAS (Análise de Origem)")
print("=" * 80)

# Classificar estações
portais = {38637: 'PORTÃO CPTM', 48848: 'Raia Olímpica', 44878: 'Portão 1 USP'}
internas_ids = [56826, 56659, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56640]

viagens_portais = sum(origens_campus[p] for p in portais.keys())
viagens_internas = sum(origens_campus[i] for i in internas_ids)

pct_portais = 100 * viagens_portais / total
pct_internas = 100 * viagens_internas / total

print(f"\nEstações-Portal (limite do campus): {viagens_portais:,} viagens ({pct_portais:.1f}%)")
for portal_id, portal_nome in portais.items():
    count = origens_campus.get(portal_id, 0)
    pct = 100 * count / total
    print(f"  - {portal_nome}: {count:,} ({pct:.1f}%)")

print(f"\nEstações Internas (central): {viagens_internas:,} viagens ({pct_internas:.1f}%)")

# ============================================================================
# 8. VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 80)
print("7. GERANDO VISUALIZAÇÕES")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Gráfico 1: Top 10 Origens no Campus
ax1 = axes[0, 0]
labels_orig = [o['nome'].split('-')[0].strip()[:20] for o in top_origens[:10]]
viagens_orig = [o['viagens'] for o in top_origens[:10]]
colors_orig = sns.color_palette("mako", len(labels_orig))

ax1.barh(range(len(labels_orig)), viagens_orig, color=colors_orig, edgecolor='black')
ax1.set_yticks(range(len(labels_orig)))
ax1.set_yticklabels(labels_orig, fontsize=9)
ax1.set_xlabel('Número de viagens', fontsize=11, fontweight='bold')
ax1.set_title('Top 10 Origens no Campus\n(De onde saem)', 
              fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(viagens_orig):
    ax1.text(v + 20, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 2: Top 15 Destinos Externos
ax2 = axes[0, 1]
labels_dest = [d['nome'].split('-')[0].strip()[:25] for d in top_destinos[:15]]
viagens_dest = [d['viagens'] for d in top_destinos[:15]]
colors_dest = sns.color_palette("rocket", len(labels_dest))

ax2.barh(range(len(labels_dest)), viagens_dest, color=colors_dest, edgecolor='black')
ax2.set_yticks(range(len(labels_dest)))
ax2.set_yticklabels(labels_dest, fontsize=9)
ax2.set_xlabel('Número de viagens', fontsize=11, fontweight='bold')
ax2.set_title('Top 15 Destinos Externos\n(Para onde vão do campus)', 
              fontsize=13, fontweight='bold', pad=15)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(viagens_dest):
    ax2.text(v + 20, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 3: Distribuição Horária
ax3 = axes[1, 0]
horas_list = list(range(24))
viagens_por_hora = [horas.get(h, 0) for h in horas_list]
colors_hora = ['#D62828' if h in [16, 17] else '#06A77D' if h == 18 else '#1E88E5' 
               for h in horas_list]

ax3.bar(horas_list, viagens_por_hora, color=colors_hora, edgecolor='black', alpha=0.8)
ax3.set_xlabel('Hora do dia', fontsize=11, fontweight='bold')
ax3.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax3.set_title('Distribuição Horária - Fluxo de Saída\n(Destaque: pico vespertino 16h-17h)', 
              fontsize=13, fontweight='bold', pad=15)
ax3.set_xticks(range(0, 24, 2))
ax3.grid(True, alpha=0.3, axis='y')

# Anotar pico
pico_hora = max(horas.items(), key=lambda x: x[1])
ax3.annotate(f'PICO\n{pico_hora[1]:,}', xy=(pico_hora[0], pico_hora[1]), 
            xytext=(pico_hora[0], pico_hora[1] + 150),
            ha='center', fontsize=10, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=2))

# Gráfico 4: Proporção Transporte Público + Portais vs Internas
ax4 = axes[1, 1]

# Duas pizzas lado a lado
# Pizza 1: Destinos (TP vs Outros)
ax4_1 = plt.subplot(2, 2, 4)
sizes1 = [total_tp, total - total_tp]
labels1 = [f'Para Transporte\nPúblico\n{total_tp:,}\n({pct_tp:.1f}%)',
           f'Outros Destinos\n{total - total_tp:,}\n({100-pct_tp:.1f}%)']
colors1 = ['#06A77D', '#1E88E5']
explode1 = (0.05, 0)

ax4_1.pie(sizes1, explode=explode1, labels=labels1, colors=colors1, autopct='',
         startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
ax4_1.set_title('Destinos: Proporção para\nTransporte Público', 
               fontsize=12, fontweight='bold', pad=10)

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_15_fluxo_saida.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# 9. ESTATÍSTICAS FINAIS
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO - FLUXO DE SAÍDA (USP → EXTERNO)")
print("=" * 80)

print(f"""
Total de viagens de saída: {total:,}

Top 3 Origens no Campus:
  1. {top_origens[0]['nome']}: {top_origens[0]['viagens']:,} viagens ({top_origens[0]['pct']:.1f}%)
  2. {top_origens[1]['nome']}: {top_origens[1]['viagens']:,} viagens ({top_origens[1]['pct']:.1f}%)
  3. {top_origens[2]['nome']}: {top_origens[2]['viagens']:,} viagens ({top_origens[2]['pct']:.1f}%)

Top 3 Destinos Externos:
  1. {top_destinos[0]['nome']}: {top_destinos[0]['viagens']:,} viagens ({top_destinos[0]['pct']:.1f}%)
  2. {top_destinos[1]['nome']}: {top_destinos[1]['viagens']:,} viagens ({top_destinos[1]['pct']:.1f}%)
  3. {top_destinos[2]['nome']}: {top_destinos[2]['viagens']:,} viagens ({top_destinos[2]['pct']:.1f}%)

Top Rota de Saída:
  {top_rotas[0]['origem']} → {top_rotas[0]['destino']}: {top_rotas[0]['viagens']:,} viagens

Viagens para transporte público: {total_tp:,} ({pct_tp:.1f}%)

Pico horário: {pico_hora[0]:02d}h com {pico_hora[1]:,} viagens ({100*pico_hora[1]/total:.1f}%)

Saídas desde portais (limite): {viagens_portais:,} ({pct_portais:.1f}%)
Saídas desde estações internas: {viagens_internas:,} ({pct_internas:.1f}%)
""")

print("=" * 80)
print("✅ ANÁLISE CONCLUÍDA")
print("=" * 80)
