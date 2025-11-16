#!/usr/bin/env python3
"""
Análise Específica: FLUXO DE ENTRADA (EXTERNO → USP)
=====================================================

Análise detalhada das viagens que começam FORA do campus e terminam DENTRO.
Foco em padrões de acesso ao campus, principais pontos de origem externos,
e comportamento de integração modal (última milha de entrada).

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
print("ANÁLISE ESPECÍFICA: FLUXO DE ENTRADA (EXTERNO → USP)")
print("=" * 80)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

print("\n📊 Carregando viagens de entrada...")
viagens_entrada = Trip.objects.filter(
    final_station_id__in=ESTACOES_USP
).exclude(
    initial_station_id__in=ESTACOES_USP
)
total = viagens_entrada.count()
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
# 2. TOP 20 ORIGENS EXTERNAS
# ============================================================================

print("\n" + "=" * 80)
print("1. TOP 20 ORIGENS EXTERNAS (De onde vêm para o campus)")
print("=" * 80)

origens_externas = Counter()
for v in viagens_entrada.values('initial_station_id', 'initial_station_name'):
    origens_externas[v['initial_station_id']] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Origem Externa'}")
print("-" * 80)

top_origens = []
for rank, (est_id, count) in enumerate(origens_externas.most_common(20), 1):
    pct = 100 * count / total
    try:
        est = Station.objects.get(id=est_id)
        nome = est.name
    except:
        # Buscar do primeiro registro com esse ID
        v = viagens_entrada.filter(initial_station_id=est_id).first()
        nome = v.initial_station_name if v else f"Estação {est_id}"
    
    print(f"{rank:<4} {count:<10,} {pct:6.2f}%  {nome}")
    top_origens.append({
        'rank': rank,
        'id': est_id,
        'nome': nome,
        'viagens': count,
        'pct': pct
    })

# ============================================================================
# 3. TOP 15 DESTINOS NO CAMPUS (Para onde vão dentro do campus)
# ============================================================================

print("\n" + "=" * 80)
print("2. TOP 15 DESTINOS NO CAMPUS (Para onde vão os que entram)")
print("=" * 80)

destinos_campus = Counter()
for v in viagens_entrada.values('final_station_id'):
    destinos_campus[v['final_station_id']] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Destino no Campus'}")
print("-" * 80)

top_destinos = []
for rank, (est_id, count) in enumerate(destinos_campus.most_common(15), 1):
    pct = 100 * count / total
    nome = estacoes_usp_map.get(est_id, f"Estação {est_id}")
    print(f"{rank:<4} {count:<10,} {pct:6.2f}%  {nome}")
    top_destinos.append({
        'rank': rank,
        'id': est_id,
        'nome': nome,
        'viagens': count,
        'pct': pct
    })

# ============================================================================
# 4. TOP 15 PARES ORIGEM-DESTINO (rotas de entrada mais usadas)
# ============================================================================

print("\n" + "=" * 80)
print("3. TOP 15 ROTAS DE ENTRADA MAIS USADAS")
print("=" * 80)

rotas_entrada = Counter()
for v in viagens_entrada.values('initial_station_id', 'initial_station_name', 'final_station_id'):
    origem_id = v['initial_station_id']
    destino_id = v['final_station_id']
    rotas_entrada[(origem_id, destino_id)] += 1

print(f"\n{'#':<4} {'Viagens':<10} {'Rota (Origem Externa → Destino Campus)'}")
print("-" * 100)

top_rotas = []
for rank, ((origem_id, destino_id), count) in enumerate(rotas_entrada.most_common(15), 1):
    pct = 100 * count / total
    
    # Nome origem
    try:
        origem_est = Station.objects.get(id=origem_id)
        origem_nome = origem_est.name
    except:
        v = viagens_entrada.filter(initial_station_id=origem_id).first()
        origem_nome = v.initial_station_name if v else f"Estação {origem_id}"
    
    destino_nome = estacoes_usp_map.get(destino_id, f"Estação {destino_id}")
    
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
print("4. DISTRIBUIÇÃO TEMPORAL DO FLUXO DE ENTRADA")
print("=" * 80)

horas = Counter()
dias = Counter()

for v in viagens_entrada.iterator():
    horas[v.start_hour] += 1
    dias[v.start_day] += 1

print("\n⏰ DISTRIBUIÇÃO POR HORA (Quando as pessoas ENTRAM no campus):")
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
# 6. IDENTIFICAR ESTAÇÕES DE TRANSPORTE PÚBLICO
# ============================================================================

print("\n" + "=" * 80)
print("5. ORIGENS DE TRANSPORTE PÚBLICO (Metrô, CPTM, Trem)")
print("=" * 80)

# Palavras-chave para identificar transporte público
palavras_tp = ['metrô', 'metro', 'cptm', 'trem', 'estacao', 'estação']

origens_tp = []
total_tp = 0

for origem in top_origens:
    nome_lower = origem['nome'].lower()
    if any(palavra in nome_lower for palavra in palavras_tp):
        origens_tp.append(origem)
        total_tp += origem['viagens']

pct_tp = 100 * total_tp / total

print(f"\n✓ Viagens de estações de transporte público: {total_tp:,} ({pct_tp:.1f}%)")
print(f"\n{'#':<4} {'Viagens':<10} {'%':<8} {'Estação de Transporte'}")
print("-" * 80)

for i, origem in enumerate(origens_tp[:10], 1):
    print(f"{i:<4} {origem['viagens']:<10,} {origem['pct']:6.2f}%  {origem['nome']}")

# ============================================================================
# 7. VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 80)
print("6. GERANDO VISUALIZAÇÕES")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Gráfico 1: Top 15 Origens Externas
ax1 = axes[0, 0]
labels = [o['nome'].split('-')[0].strip()[:25] for o in top_origens[:15]]
viagens = [o['viagens'] for o in top_origens[:15]]
colors = sns.color_palette("rocket", len(labels))

ax1.barh(range(len(labels)), viagens, color=colors, edgecolor='black')
ax1.set_yticks(range(len(labels)))
ax1.set_yticklabels(labels, fontsize=9)
ax1.set_xlabel('Número de viagens', fontsize=11, fontweight='bold')
ax1.set_title('Top 15 Origens Externas\n(De onde vêm para o campus)', 
              fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
ax1.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(viagens):
    ax1.text(v + 20, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 2: Top 10 Destinos no Campus
ax2 = axes[0, 1]
labels_dest = [d['nome'].split('-')[0].strip()[:20] for d in top_destinos[:10]]
viagens_dest = [d['viagens'] for d in top_destinos[:10]]
colors_dest = sns.color_palette("mako", len(labels_dest))

ax2.barh(range(len(labels_dest)), viagens_dest, color=colors_dest, edgecolor='black')
ax2.set_yticks(range(len(labels_dest)))
ax2.set_yticklabels(labels_dest, fontsize=9)
ax2.set_xlabel('Número de viagens', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Destinos no Campus\n(Para onde vão os que entram)', 
              fontsize=13, fontweight='bold', pad=15)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(viagens_dest):
    ax2.text(v + 10, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 3: Distribuição Horária
ax3 = axes[1, 0]
horas_list = list(range(24))
viagens_por_hora = [horas.get(h, 0) for h in horas_list]
colors_hora = ['#D62828' if h == 7 else '#06A77D' if h in [8, 18] else '#1E88E5' 
               for h in horas_list]

ax3.bar(horas_list, viagens_por_hora, color=colors_hora, edgecolor='black', alpha=0.8)
ax3.set_xlabel('Hora do dia', fontsize=11, fontweight='bold')
ax3.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax3.set_title('Distribuição Horária - Fluxo de Entrada\n(Destaque: pico matinal às 7h)', 
              fontsize=13, fontweight='bold', pad=15)
ax3.set_xticks(range(0, 24, 2))
ax3.grid(True, alpha=0.3, axis='y')

# Anotar pico
pico_hora = max(horas.items(), key=lambda x: x[1])
ax3.annotate(f'PICO\n{pico_hora[1]:,}', xy=(pico_hora[0], pico_hora[1]), 
            xytext=(pico_hora[0], pico_hora[1] + 150),
            ha='center', fontsize=10, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=2))

# Gráfico 4: Proporção Transporte Público
ax4 = axes[1, 1]
sizes = [total_tp, total - total_tp]
labels_pie = [f'Transporte Público\n(Metrô, CPTM, etc.)\n{total_tp:,}\n({pct_tp:.1f}%)',
              f'Outras Origens\n{total - total_tp:,}\n({100-pct_tp:.1f}%)']
colors_pie = ['#06A77D', '#1E88E5']
explode = (0.05, 0)

ax4.pie(sizes, explode=explode, labels=labels_pie, colors=colors_pie, autopct='',
        startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax4.set_title('Proporção de Viagens desde\nEstações de Transporte Público', 
              fontsize=13, fontweight='bold', pad=15)

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_14_fluxo_entrada.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# 8. ESTATÍSTICAS FINAIS
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO - FLUXO DE ENTRADA (EXTERNO → USP)")
print("=" * 80)

print(f"""
Total de viagens de entrada: {total:,}

Top 3 Origens Externas:
  1. {top_origens[0]['nome']}: {top_origens[0]['viagens']:,} viagens ({top_origens[0]['pct']:.1f}%)
  2. {top_origens[1]['nome']}: {top_origens[1]['viagens']:,} viagens ({top_origens[1]['pct']:.1f}%)
  3. {top_origens[2]['nome']}: {top_origens[2]['viagens']:,} viagens ({top_origens[2]['pct']:.1f}%)

Top 3 Destinos no Campus:
  1. {top_destinos[0]['nome']}: {top_destinos[0]['viagens']:,} viagens ({top_destinos[0]['pct']:.1f}%)
  2. {top_destinos[1]['nome']}: {top_destinos[1]['viagens']:,} viagens ({top_destinos[1]['pct']:.1f}%)
  3. {top_destinos[2]['nome']}: {top_destinos[2]['viagens']:,} viagens ({top_destinos[2]['pct']:.1f}%)

Top Rota de Entrada:
  {top_rotas[0]['origem']} → {top_rotas[0]['destino']}: {top_rotas[0]['viagens']:,} viagens

Viagens desde transporte público: {total_tp:,} ({pct_tp:.1f}%)

Pico horário: {pico_hora[0]:02d}h com {pico_hora[1]:,} viagens ({100*pico_hora[1]/total:.1f}%)
""")

print("=" * 80)
print("✅ ANÁLISE CONCLUÍDA")
print("=" * 80)
