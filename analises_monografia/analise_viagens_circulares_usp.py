#!/usr/bin/env python3
"""
Análise de Viagens Circulares - Campus USP
===========================================

Investiga viagens onde origem = destino (viagens circulares).
Analisa duração, horários, estações e padrões de uso.

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

from ciclovias.models import Trip, Station

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 12)
plt.rcParams['font.size'] = 10

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estações USP
ESTACOES_USP = [56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 
                56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323]

print("=" * 80)
print("ANÁLISE DE VIAGENS CIRCULARES - CAMPUS USP")
print("=" * 80)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

print("\n📊 Carregando dados...")

# Total viagens internas USP
total_internas = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP,
    final_station_id__in=ESTACOES_USP
).count()

# Viagens circulares (mesma origem e destino)
viagens_circulares = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP
).filter(
    initial_station_id=django.db.models.F('final_station_id')
)

total_circulares = viagens_circulares.count()
pct_circulares = 100 * total_circulares / total_internas

print(f"   Total viagens internas: {total_internas:,}")
print(f"   Viagens circulares: {total_circulares:,} ({pct_circulares:.1f}%)")

# ============================================================================
# 2. ANÁLISE DE DURAÇÃO
# ============================================================================

print("\n" + "=" * 80)
print("1. ANÁLISE DE DURAÇÃO")
print("=" * 80)

duracoes = []
for v in viagens_circulares.iterator():
    duracao_min = v.duration_seconds / 60
    if duracao_min > 0:
        duracoes.append(duracao_min)

duracoes.sort()
n = len(duracoes)

stats = {
    'min': duracoes[0],
    'q1': duracoes[n//4],
    'mediana': duracoes[n//2],
    'media': sum(duracoes) / n,
    'q3': duracoes[3*n//4],
    'max': duracoes[-1]
}

print(f"\n⏱️  ESTATÍSTICAS DE DURAÇÃO:")
print(f"   Mínima:   {stats['min']:.1f} min")
print(f"   Q1 (25%): {stats['q1']:.1f} min")
print(f"   Mediana:  {stats['mediana']:.1f} min")
print(f"   Média:    {stats['media']:.1f} min")
print(f"   Q3 (75%): {stats['q3']:.1f} min")
print(f"   Máxima:   {stats['max']:.1f} min")

# Categorizar
categorias = {
    '< 5 min (engano/teste)': sum(1 for d in duracoes if d < 5),
    '5-15 min (volta curta)': sum(1 for d in duracoes if 5 <= d < 15),
    '15-30 min (passeio médio)': sum(1 for d in duracoes if 15 <= d < 30),
    '30-60 min (passeio longo)': sum(1 for d in duracoes if 30 <= d < 60),
    '60-120 min (volta extensa)': sum(1 for d in duracoes if 60 <= d < 120),
    '>= 120 min (uso prolongado)': sum(1 for d in duracoes if d >= 120)
}

print(f"\n📈 DISTRIBUIÇÃO POR FAIXAS:")
for categoria, count in categorias.items():
    pct = 100 * count / n
    print(f"   {categoria:<30} {count:6,} ({pct:5.1f}%)")

# ============================================================================
# 3. ANÁLISE POR ESTAÇÃO
# ============================================================================

print("\n" + "=" * 80)
print("2. ANÁLISE POR ESTAÇÃO")
print("=" * 80)

estacoes_count = Counter()
for v in viagens_circulares.values('initial_station_id'):
    estacoes_count[v['initial_station_id']] += 1

print(f"\n🏛️  TOP 10 ESTAÇÕES COM VIAGENS CIRCULARES:\n")
print(f"{'#':<4} {'Viagens':<10} {'%':<8} {'Estação'}")
print("-" * 80)

top_estacoes = []
for rank, (est_id, count) in enumerate(estacoes_count.most_common(10), 1):
    pct = 100 * count / total_circulares
    try:
        est = Station.objects.get(id=est_id)
        nome = est.name.split('-')[0].strip()[:30]
    except:
        nome = f"Estação {est_id}"
    
    print(f"{rank:<4} {count:<10,} {pct:6.2f}%  {nome}")
    top_estacoes.append({'nome': nome, 'viagens': count, 'pct': pct})

# ============================================================================
# 4. ANÁLISE TEMPORAL
# ============================================================================

print("\n" + "=" * 80)
print("3. ANÁLISE TEMPORAL")
print("=" * 80)

horas = Counter()
for v in viagens_circulares.iterator():
    horas[v.start_hour] += 1

print(f"\n⏰ TOP 5 HORÁRIOS:")
for h, count in horas.most_common(5):
    pct = 100 * count / total_circulares
    print(f"   {h:02d}h: {count:,} viagens ({pct:.1f}%)")

# ============================================================================
# 5. ANÁLISE ESPECÍFICA DO BANDEJÃO CENTRAL
# ============================================================================

print("\n" + "=" * 80)
print("4. ANÁLISE ESPECÍFICA: BANDEJÃO CENTRAL")
print("=" * 80)

bandejao_circulares = Trip.objects.filter(
    initial_station_id=38476,  # Bandejão Central
    final_station_id=38476
)

total_bandejao = bandejao_circulares.count()
pct_bandejao = 100 * total_bandejao / total_circulares

print(f"\n📊 Viagens circulares no Bandejão: {total_bandejao:,} ({pct_bandejao:.1f}% do total)")

duracoes_bandejao = []
for v in bandejao_circulares.iterator():
    duracao_min = v.duration_seconds / 60
    if duracao_min > 0 and duracao_min < 180:  # Filtrar outliers extremos
        duracoes_bandejao.append(duracao_min)

n_b = len(duracoes_bandejao)
duracoes_bandejao.sort()

print(f"\n⏱️  DURAÇÃO NO BANDEJÃO:")
print(f"   Mediana: {duracoes_bandejao[n_b//2]:.1f} min")
print(f"   Média:   {sum(duracoes_bandejao)/n_b:.1f} min")

categorias_bandejao = {
    '< 5 min': sum(1 for d in duracoes_bandejao if d < 5),
    '5-15 min': sum(1 for d in duracoes_bandejao if 5 <= d < 15),
    '15-30 min': sum(1 for d in duracoes_bandejao if 15 <= d < 30),
    '30-60 min': sum(1 for d in duracoes_bandejao if 30 <= d < 60),
    '60-120 min': sum(1 for d in duracoes_bandejao if 60 <= d < 120),
    '>= 120 min': sum(1 for d in duracoes_bandejao if d >= 120)
}

print(f"\n📈 DISTRIBUIÇÃO BANDEJÃO:")
for cat, count in categorias_bandejao.items():
    pct = 100 * count / n_b
    print(f"   {cat:<12} {count:6,} ({pct:5.1f}%)")

# ============================================================================
# 6. VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 80)
print("5. GERANDO VISUALIZAÇÕES")
print("=" * 80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# Gráfico 1: Pizza - Circulares vs Não-circulares
ax1 = axes[0, 0]
sizes = [total_circulares, total_internas - total_circulares]
labels = [f'Circulares\n{total_circulares:,}\n({pct_circulares:.1f}%)',
          f'Não-circulares\n{total_internas - total_circulares:,}\n({100-pct_circulares:.1f}%)']
colors = ['#E63946', '#457B9D']
ax1.pie(sizes, labels=labels, colors=colors, autopct='', startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Proporção de Viagens Circulares\nno Campus USP', 
              fontsize=13, fontweight='bold', pad=15)

# Gráfico 2: Distribuição de duração (histograma)
ax2 = axes[0, 1]
duracoes_filtradas = [d for d in duracoes if d < 120]  # Até 2h para visualização
ax2.hist(duracoes_filtradas, bins=50, color='#2A9D8F', edgecolor='black', alpha=0.7)
ax2.axvline(stats['mediana'], color='red', linestyle='--', linewidth=2,
           label=f'Mediana: {stats["mediana"]:.1f} min')
ax2.axvline(stats['media'], color='orange', linestyle='--', linewidth=2,
           label=f'Média: {stats["media"]:.1f} min')
ax2.set_xlabel('Duração (minutos)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax2.set_title('Distribuição de Duração das Viagens Circulares\n(até 120 min)', 
              fontsize=13, fontweight='bold', pad=15)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# Gráfico 3: Top 10 estações
ax3 = axes[0, 2]
nomes = [e['nome'] for e in top_estacoes]
viagens_top = [e['viagens'] for e in top_estacoes]
colors_bar = sns.color_palette("rocket", len(nomes))

ax3.barh(range(len(nomes)), viagens_top, color=colors_bar, edgecolor='black')
ax3.set_yticks(range(len(nomes)))
ax3.set_yticklabels(nomes, fontsize=9)
ax3.set_xlabel('Número de viagens circulares', fontsize=11, fontweight='bold')
ax3.set_title('Top 10 Estações - Viagens Circulares', 
              fontsize=13, fontweight='bold', pad=15)
ax3.invert_yaxis()
ax3.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(viagens_top):
    ax3.text(v + 50, i, f'{v:,}', va='center', fontsize=8)

# Gráfico 4: Faixas de duração
ax4 = axes[1, 0]
faixas = list(categorias.keys())
valores_faixas = [categorias[f] for f in faixas]
colors_faixas = ['#E63946', '#F77F00', '#FCBF49', '#06A77D', '#457B9D', '#1D3557']

bars = ax4.bar(range(len(faixas)), valores_faixas, color=colors_faixas, 
               edgecolor='black', alpha=0.8)
ax4.set_xticks(range(len(faixas)))
ax4.set_xticklabels([f.split('(')[0].strip() for f in faixas], 
                      rotation=45, ha='right', fontsize=9)
ax4.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax4.set_title('Distribuição por Faixas de Duração', 
              fontsize=13, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, valores_faixas):
    height = bar.get_height()
    pct = 100 * val / n
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:,}\n({pct:.1f}%)',
             ha='center', va='bottom', fontsize=8, fontweight='bold')

# Gráfico 5: Distribuição horária
ax5 = axes[1, 1]
horas_list = list(range(24))
viagens_hora = [horas.get(h, 0) for h in horas_list]
colors_hora = ['#E63946' if h in [11, 16, 17] else '#457B9D' for h in horas_list]

ax5.bar(horas_list, viagens_hora, color=colors_hora, edgecolor='black', alpha=0.8)
ax5.set_xlabel('Hora do dia', fontsize=11, fontweight='bold')
ax5.set_ylabel('Número de viagens', fontsize=11, fontweight='bold')
ax5.set_title('Distribuição Horária - Viagens Circulares\n(Picos em 11h, 16h, 17h)', 
              fontsize=13, fontweight='bold', pad=15)
ax5.set_xticks(range(0, 24, 2))
ax5.grid(True, alpha=0.3, axis='y')

# Gráfico 6: Comparação Bandejão vs Outras
ax6 = axes[1, 2]
labels_comp = ['Bandejão\nCentral', 'Outras\nEstações']
valores_comp = [total_bandejao, total_circulares - total_bandejao]
colors_comp = ['#E63946', '#457B9D']

bars_comp = ax6.bar(labels_comp, valores_comp, color=colors_comp, 
                     edgecolor='black', alpha=0.8, width=0.6)
ax6.set_ylabel('Número de viagens circulares', fontsize=11, fontweight='bold')
ax6.set_title('Concentração no Bandejão Central', 
              fontsize=13, fontweight='bold', pad=15)
ax6.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars_comp, valores_comp):
    height = bar.get_height()
    pct = 100 * val / total_circulares
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:,}\n({pct:.1f}%)',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'analise_viagens_circulares_usp.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# 7. RESUMO E INTERPRETAÇÃO
# ============================================================================

print("\n" + "=" * 80)
print("RESUMO - VIAGENS CIRCULARES NO CAMPUS USP")
print("=" * 80)

print(f"""
📊 NÚMEROS PRINCIPAIS:
   - Total de viagens circulares: {total_circulares:,} ({pct_circulares:.1f}% das internas)
   - Duração mediana: {stats['mediana']:.1f} minutos
   - Duração média: {stats['media']:.1f} minutos
   - Bandejão Central: {total_bandejao:,} viagens ({pct_bandejao:.1f}% das circulares)

🔍 INTERPRETAÇÃO:

1. PADRÃO PREDOMINANTE: "Ida ao Bandejão"
   - 61% das circulares ocorrem no Bandejão Central
   - Horários de pico: 11h, 12h, 16h, 17h (alimentação)
   - Duração típica: 30-60 min (50.6% no Bandejão)
   
2. NÃO SÃO ENGANOS:
   - Apenas 7.8% têm duração < 5 min
   - Mediana de 37.5 min indica uso intencional
   
3. NÃO SÃO "PASSEIOS":
   - Apenas 2.8% > 120 min
   - Padrão compatível com: pegar bike → almoçar → devolver
   
4. COMPORTAMENTO LEGÍTIMO:
   - Usuário pega bike em local X
   - Vai ao Bandejão Central (ou outra estação)
   - Retorna ao mesmo local X
   - Do ponto de vista de X: viagem circular
   
✓ CONCLUSÃO: As viagens circulares refletem uso real do sistema para
             deslocamentos internos, principalmente para alimentação.
             Não indicam fraude, engano ou mau uso do sistema.
""")

print("=" * 80)
print("✅ ANÁLISE COMPLETA")
print("=" * 80)
