#!/usr/bin/env python3
"""
Análise de Distribuição de Duração das Viagens - Campus USP
============================================================

Gráfico mostrando quantas viagens há em cada faixa de duração específica.
Faixas: < 1 min, < 3 min, < 5 min, < 7 min, < 10 min, < 20 min, 
        < 30 min, < 40 min, >= 40 min

Autor: Gabriel
Data: Novembro 2024
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from ciclovias.models import Trip

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (18, 10)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estações USP
ESTACOES_USP = [56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 
                56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323]

print("=" * 80)
print("ANÁLISE DE DURAÇÃO DAS VIAGENS - CAMPUS USP")
print("=" * 80)

# ============================================================================
# 1. CARREGAR VIAGENS INTERNAS USP
# ============================================================================

print("\n📊 Carregando viagens internas USP...")

viagens_usp = Trip.objects.filter(
    initial_station_id__in=ESTACOES_USP,
    final_station_id__in=ESTACOES_USP
)

total_viagens = viagens_usp.count()
print(f"   Total de viagens internas: {total_viagens:,}")

# ============================================================================
# 2. EXTRAIR DURAÇÕES
# ============================================================================

print("\n⏱️  Processando durações...")

duracoes_minutos = []
for v in viagens_usp.iterator():
    duracao_min = v.duration_seconds / 60.0
    if duracao_min > 0:  # Filtrar valores inválidos
        duracoes_minutos.append(duracao_min)

print(f"   Viagens processadas: {len(duracoes_minutos):,}")

# ============================================================================
# 3. CATEGORIZAR POR FAIXAS
# ============================================================================

print("\n📈 Categorizando por faixas de duração...")

# Definir as faixas exatamente como solicitado
faixas = {
    '< 1 min': 0,
    '1-3 min': 0,
    '3-5 min': 0,
    '5-7 min': 0,
    '7-10 min': 0,
    '10-20 min': 0,
    '20-30 min': 0,
    '30-40 min': 0,
    '≥ 40 min': 0
}

for duracao in duracoes_minutos:
    if duracao < 1:
        faixas['< 1 min'] += 1
    elif duracao < 3:
        faixas['1-3 min'] += 1
    elif duracao < 5:
        faixas['3-5 min'] += 1
    elif duracao < 7:
        faixas['5-7 min'] += 1
    elif duracao < 10:
        faixas['7-10 min'] += 1
    elif duracao < 20:
        faixas['10-20 min'] += 1
    elif duracao < 30:
        faixas['20-30 min'] += 1
    elif duracao < 40:
        faixas['30-40 min'] += 1
    else:
        faixas['≥ 40 min'] += 1

# Calcular percentuais
total_categorizado = sum(faixas.values())
faixas_pct = {k: 100 * v / total_categorizado for k, v in faixas.items()}

# ============================================================================
# 4. EXIBIR RESULTADOS
# ============================================================================

print("\n" + "=" * 80)
print("DISTRIBUIÇÃO POR FAIXAS DE DURAÇÃO")
print("=" * 80)

print(f"\n{'Faixa de Duração':<15} {'Viagens':<12} {'%':<8} {'Barra'}")
print("-" * 80)

for faixa in faixas.keys():
    count = faixas[faixa]
    pct = faixas_pct[faixa]
    barra = '█' * int(pct)
    print(f"{faixa:<15} {count:<12,} {pct:6.2f}%  {barra}")

print("-" * 80)
print(f"{'TOTAL':<15} {total_categorizado:<12,} {100.0:6.2f}%")

# ============================================================================
# 5. ESTATÍSTICAS GERAIS
# ============================================================================

duracoes_minutos.sort()
n = len(duracoes_minutos)

print("\n" + "=" * 80)
print("ESTATÍSTICAS GERAIS DE DURAÇÃO")
print("=" * 80)

print(f"\n⏱️  MEDIDAS:")
print(f"   Mínima:   {duracoes_minutos[0]:.2f} minutos")
print(f"   Q1 (25%): {duracoes_minutos[n//4]:.2f} minutos")
print(f"   Mediana:  {duracoes_minutos[n//2]:.2f} minutos")
print(f"   Média:    {sum(duracoes_minutos)/n:.2f} minutos")
print(f"   Q3 (75%): {duracoes_minutos[3*n//4]:.2f} minutos")
print(f"   Máxima:   {duracoes_minutos[-1]:.2f} minutos")

# ============================================================================
# 6. CRIAR GRÁFICOS
# ============================================================================

print("\n" + "=" * 80)
print("GERANDO VISUALIZAÇÕES (ARQUIVOS INDIVIDUAIS)")
print("=" * 80)

# Gráfico 1: Barras - Distribuição por faixas
plt.figure(figsize=(12, 8))
faixas_labels = list(faixas.keys())
faixas_valores = list(faixas.values())
colors1 = ['#E63946' if '<' in f or '1-3' in f else '#F77F00' if '3-5' in f or '5-7' in f 
           else '#06A77D' if '10-20' in f or '20-30' in f or '30-40' in f 
           else '#1E88E5' for f in faixas_labels]

bars1 = plt.bar(range(len(faixas_labels)), faixas_valores, color=colors1, 
                edgecolor='black', alpha=0.8, width=0.7)
plt.xticks(range(len(faixas_labels)), faixas_labels, rotation=45, ha='right', fontsize=10)
plt.ylabel('Número de viagens', fontsize=12, fontweight='bold')
plt.title('Distribuição de Viagens por Faixa de Duração\nCampus USP - {:,} viagens'.format(total_categorizado), 
              fontsize=14, fontweight='bold', pad=15)
plt.grid(True, alpha=0.3, axis='y')

# Adicionar valores nas barras
for bar, val in zip(bars1, faixas_valores):
    height = bar.get_height()
    pct = 100 * val / total_categorizado
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:,}\n({pct:.1f}%)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'distribuicao_duracao_barras.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Gráfico salvo: {output_path}")
plt.close()

# Gráfico 2: Pizza - Proporções
plt.figure(figsize=(10, 10))
# Agrupar algumas faixas para melhor visualização
grupos = {
    'Muito curta\n(< 3 min)': faixas['< 1 min'] + faixas['1-3 min'],
    'Curta\n(3-10 min)': faixas['3-5 min'] + faixas['5-7 min'] + faixas['7-10 min'],
    'Média\n(10-30 min)': faixas['10-20 min'] + faixas['20-30 min'],
    'Longa\n(30-40 min)': faixas['30-40 min'],
    'Muito longa\n(≥ 40 min)': faixas['≥ 40 min']
}

colors_pie = ['#E63946', '#F77F00', '#06A77D', '#457B9D', '#1E88E5']
explode = (0.05, 0, 0, 0, 0)

wedges, texts, autotexts = plt.pie(grupos.values(), labels=grupos.keys(), colors=colors_pie, 
                                     autopct='%1.1f%%', startangle=90, explode=explode,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})
plt.title('Proporção por Grupos de Duração', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'distribuicao_duracao_pizza.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Gráfico salvo: {output_path}")
plt.close()

# Gráfico 3: Histograma detalhado (até 60 min)
plt.figure(figsize=(12, 8))
duracoes_ate_60 = [d for d in duracoes_minutos if d <= 60]
plt.hist(duracoes_ate_60, bins=60, color='#2A9D8F', edgecolor='black', alpha=0.7, linewidth=0.5)
plt.axvline(sum(duracoes_minutos)/n, color='red', linestyle='--', linewidth=2,
           label=f'Média: {sum(duracoes_minutos)/n:.1f} min')
plt.axvline(duracoes_minutos[n//2], color='orange', linestyle='--', linewidth=2,
           label=f'Mediana: {duracoes_minutos[n//2]:.1f} min')
plt.xlabel('Duração (minutos)', fontsize=12, fontweight='bold')
plt.ylabel('Número de viagens', fontsize=12, fontweight='bold')
plt.title('Histograma Detalhado de Duração\n(viagens até 60 minutos)', 
              fontsize=14, fontweight='bold', pad=15)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, axis='y')
plt.xlim(0, 60)
plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'distribuicao_duracao_histograma.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Gráfico salvo: {output_path}")
plt.close()

# Gráfico 4: Percentuais acumulados
plt.figure(figsize=(12, 8))
faixas_acumulado = []
acumulado = 0
for faixa in faixas_labels:
    acumulado += faixas_pct[faixa]
    faixas_acumulado.append(acumulado)

plt.plot(range(len(faixas_labels)), faixas_acumulado, marker='o', 
         linewidth=3, markersize=8, color='#1E88E5')
plt.fill_between(range(len(faixas_labels)), faixas_acumulado, alpha=0.3, color='#1E88E5')
plt.xticks(range(len(faixas_labels)), faixas_labels, rotation=45, ha='right', fontsize=10)
plt.ylabel('Percentual Acumulado (%)', fontsize=12, fontweight='bold')
plt.title('Percentual Acumulado por Faixa de Duração', 
              fontsize=14, fontweight='bold', pad=15)
plt.grid(True, alpha=0.3)
plt.ylim(0, 105)

# Adicionar valores nos pontos
for i, (x, y) in enumerate(zip(range(len(faixas_labels)), faixas_acumulado)):
    plt.text(x, y + 2, f'{y:.1f}%', ha='center', fontsize=8, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(OUTPUT_DIR, 'distribuicao_duracao_acumulado.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Gráfico salvo: {output_path}")
plt.close()

# ============================================================================
# 7. INSIGHTS
# ============================================================================

print("\n" + "=" * 80)
print("INSIGHTS - DISTRIBUIÇÃO DE DURAÇÃO")
print("=" * 80)

# Encontrar faixa predominante
faixa_max = max(faixas.items(), key=lambda x: x[1])
viagens_ate_10 = sum([faixas[f] for f in ['< 1 min', '1-3 min', '3-5 min', '5-7 min', '7-10 min']])
viagens_10_30 = faixas['10-20 min'] + faixas['20-30 min']
viagens_longas = faixas['30-40 min'] + faixas['≥ 40 min']

print(f"""
📊 PRINCIPAIS DESCOBERTAS:

1. FAIXA PREDOMINANTE:
   {faixa_max[0]}: {faixa_max[1]:,} viagens ({faixas_pct[faixa_max[0]]:.1f}%)

2. AGRUPAMENTOS:
   • Viagens curtas (< 10 min):     {viagens_ate_10:,} ({100*viagens_ate_10/total_categorizado:.1f}%)
   • Viagens médias (10-30 min):    {viagens_10_30:,} ({100*viagens_10_30/total_categorizado:.1f}%)
   • Viagens longas (≥ 30 min):     {viagens_longas:,} ({100*viagens_longas/total_categorizado:.1f}%)

3. ESTATÍSTICAS:
   • Duração média:   {sum(duracoes_minutos)/n:.1f} minutos
   • Duração mediana: {duracoes_minutos[n//2]:.1f} minutos
   • 50% das viagens têm entre {duracoes_minutos[n//4]:.1f} e {duracoes_minutos[3*n//4]:.1f} minutos

4. VIAGENS MUITO CURTAS (< 1 min):
   {faixas['< 1 min']:,} viagens ({faixas_pct['< 1 min']:.1f}%)
   → Possíveis desistências ou retiradas acidentais
""")

print("=" * 80)
print("✅ ANÁLISE COMPLETA")
print("=" * 80)
