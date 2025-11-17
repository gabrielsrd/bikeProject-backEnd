#!/usr/bin/env python3
"""
Script 04: Análise de Fluxos entre Estações
=============================================

Este script analisa os fluxos de viagens entre estações:
- Rotas mais frequentes (origem → destino)
- Matriz origem-destino
- Fluxos internos vs externos da USP
- Visualização de rede de conexões

Gera gráficos e dados para a monografia.

Autor: Gabriel da Silva Alves
Data: Novembro 2025
Projeto: TCC - Análise de viagens de bicicletas compartilhadas na USP
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Count, Q

# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Criar diretório de saída
OUTPUT_DIR = 'analises_monografia/resultados/graficos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analisar_fluxos_principais():
    """Identifica as rotas mais frequentes"""
    print("\n" + "="*80)
    print("  ANÁLISE DE FLUXOS - ROTAS MAIS FREQUENTES")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks)
    
    # Contar viagens por par origem-destino
    fluxos_dict = defaultdict(int)
    
    viagens = Trip.objects.filter(
        Q(initial_station__in=estacoes_usp) | Q(final_station__in=estacoes_usp)
    ).select_related('initial_station', 'final_station')
    
    print(f"\n📊 Processando {viagens.count():,} viagens...")
    
    for viagem in viagens:
        if viagem.initial_station and viagem.final_station:
            origem_id = viagem.initial_station.station_id
            destino_id = viagem.final_station.station_id
            origem_nome = viagem.initial_station.name
            destino_nome = viagem.final_station.name
            
            if origem_id != destino_id:  # Ignorar viagens que começam e terminam na mesma estação
                chave = (origem_id, destino_id, origem_nome, destino_nome)
                fluxos_dict[chave] += 1
    
    # Converter para DataFrame e ordenar
    fluxos = []
    for (orig_id, dest_id, orig_nome, dest_nome), count in fluxos_dict.items():
        fluxos.append({
            'origem_id': orig_id,
            'destino_id': dest_id,
            'origem_nome': orig_nome,
            'destino_nome': dest_nome,
            'viagens': count
        })
    
    df_fluxos = pd.DataFrame(fluxos).sort_values('viagens', ascending=False)
    
    print(f"\n📊 Total de pares origem-destino únicos: {len(df_fluxos):,}")
    print(f"📊 Total de viagens: {df_fluxos['viagens'].sum():,}")
    
    # Top 20 rotas
    top20 = df_fluxos.head(20)
    print(f"\n🏆 TOP 20 ROTAS MAIS FREQUENTES:")
    print("-" * 100)
    for i, row in top20.iterrows():
        print(f"  {row['viagens']:6,} viagens | "
              f"{row['origem_id']:3d} {row['origem_nome'][:30]:30s} → "
              f"{row['destino_id']:3d} {row['destino_nome'][:30]:30s}")
    
    # Gráfico
    plt.figure(figsize=(14, 10))
    
    # Criar labels
    labels = [f"{row['origem_id']} → {row['destino_id']}\n"
              f"{row['origem_nome'][:20]} → {row['destino_nome'][:20]}" 
              for _, row in top20.iterrows()]
    
    y_pos = np.arange(len(top20))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(top20)))
    
    bars = plt.barh(y_pos, top20['viagens'], color=colors, alpha=0.8, edgecolor='black')
    plt.yticks(y_pos, labels, fontsize=8)
    plt.xlabel('Número de Viagens', fontsize=12, fontweight='bold')
    plt.ylabel('Rota (Origem → Destino)', fontsize=12, fontweight='bold')
    plt.title('Top 20 Rotas Mais Frequentes', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, viagens in zip(bars, top20['viagens']):
        plt.text(bar.get_width() + top20['viagens'].max()*0.01, 
                bar.get_y() + bar.get_height()/2,
                f'{viagens:,}', va='center', fontsize=8)
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/top20_rotas_frequentes.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../fluxos_completos.csv'
    df_fluxos.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados completos salvos: {csv_path}")
    
    csv_top20 = f'{OUTPUT_DIR}/../top20_rotas.csv'
    top20.to_csv(csv_top20, index=False, encoding='utf-8')
    print(f"✅ Top 20 salvo: {csv_top20}")
    
    return df_fluxos

def fluxos_internos_externos():
    """Analisa fluxos internos (USP→USP) vs externos (USP↔Fora)"""
    print("\n" + "="*80)
    print("  FLUXOS INTERNOS vs EXTERNOS")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks)
    estacoes_usp_ids = set(estacoes_usp.values_list('station_id', flat=True))
    
    # Categorizar viagens
    internos = 0  # USP → USP
    saindo = 0    # USP → Fora
    chegando = 0  # Fora → USP
    
    viagens = Trip.objects.filter(
        Q(initial_station__in=estacoes_usp) | Q(final_station__in=estacoes_usp)
    ).select_related('initial_station', 'final_station')
    
    for viagem in viagens:
        if viagem.initial_station and viagem.final_station:
            origem_usp = viagem.initial_station.station_id in estacoes_usp_ids
            destino_usp = viagem.final_station.station_id in estacoes_usp_ids
            
            if origem_usp and destino_usp:
                internos += 1
            elif origem_usp and not destino_usp:
                saindo += 1
            elif not origem_usp and destino_usp:
                chegando += 1
    
    total = internos + saindo + chegando
    
    print(f"\n📊 DISTRIBUIÇÃO DE FLUXOS:")
    print(f"   • Internos (USP → USP): {internos:,} ({internos/total*100:.1f}%)")
    print(f"   • Saindo (USP → Fora): {saindo:,} ({saindo/total*100:.1f}%)")
    print(f"   • Chegando (Fora → USP): {chegando:,} ({chegando/total*100:.1f}%)")
    print(f"   • Total: {total:,}")
    
    # Gráfico de pizza
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Pizza 1: Três categorias
    sizes = [internos, saindo, chegando]
    labels = ['Internos\n(USP → USP)', 'Saindo\n(USP → Fora)', 'Chegando\n(Fora → USP)']
    colors = ['#66b3ff', '#ff9999', '#99ff99']
    explode = (0.05, 0, 0)
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Distribuição de Fluxos USP', fontsize=14, fontweight='bold')
    
    # Pizza 2: Internos vs Externos
    internos_total = internos
    externos_total = saindo + chegando
    sizes2 = [internos_total, externos_total]
    labels2 = ['Internos\n(USP → USP)', 'Externos\n(USP ↔ Fora)']
    colors2 = ['#66b3ff', '#ffcc99']
    explode2 = (0.05, 0)
    
    ax2.pie(sizes2, explode=explode2, labels=labels2, colors=colors2, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('Internos vs Externos', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/fluxos_internos_externos.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar estatísticas
    df_stats = pd.DataFrame({
        'categoria': ['Internos (USP→USP)', 'Saindo (USP→Fora)', 'Chegando (Fora→USP)'],
        'viagens': [internos, saindo, chegando],
        'percentual': [internos/total*100, saindo/total*100, chegando/total*100]
    })
    
    csv_path = f'{OUTPUT_DIR}/../fluxos_internos_externos.csv'
    df_stats.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df_stats

def matriz_origem_destino_usp():
    """Cria matriz origem-destino apenas para estações USP"""
    print("\n" + "="*80)
    print("  MATRIZ ORIGEM-DESTINO (ESTAÇÕES USP)")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    # Criar mapeamento id -> índice
    estacoes_ids = [e.station_id for e in estacoes_usp]
    estacoes_nomes = [f"{e.station_id}-{e.name[:15]}" for e in estacoes_usp]
    id_to_idx = {e_id: idx for idx, e_id in enumerate(estacoes_ids)}
    
    # Inicializar matriz
    n = len(estacoes_ids)
    matriz = np.zeros((n, n))
    
    # Preencher matriz
    viagens_usp_usp = Trip.objects.filter(
        initial_station__in=estacoes_usp,
        final_station__in=estacoes_usp
    ).select_related('initial_station', 'final_station')
    
    for viagem in viagens_usp_usp:
        if viagem.initial_station and viagem.final_station:
            orig_id = viagem.initial_station.station_id
            dest_id = viagem.final_station.station_id
            
            if orig_id in id_to_idx and dest_id in id_to_idx:
                i = id_to_idx[orig_id]
                j = id_to_idx[dest_id]
                matriz[i, j] += 1
    
    # Criar DataFrame
    df_matriz = pd.DataFrame(matriz, index=estacoes_nomes, columns=estacoes_nomes)
    
    print(f"\n📊 Matriz {n}x{n} criada")
    print(f"📊 Total de viagens internas: {matriz.sum():,.0f}")
    print(f"📊 Rota mais frequente: {matriz.max():,.0f} viagens")
    
    # Heatmap
    plt.figure(figsize=(16, 14))
    
    # Usar log scale para melhor visualização
    matriz_log = np.log10(matriz + 1)  # +1 para evitar log(0)
    
    sns.heatmap(matriz_log, annot=False, fmt='.0f', cmap='YlOrRd',
                xticklabels=estacoes_nomes, yticklabels=estacoes_nomes,
                cbar_kws={'label': 'log10(Viagens + 1)'},
                linewidths=0.5, linecolor='white')
    
    plt.xlabel('Destino', fontsize=12, fontweight='bold')
    plt.ylabel('Origem', fontsize=12, fontweight='bold')
    plt.title('Matriz Origem-Destino (Estações USP) - Escala Logarítmica', 
              fontsize=14, fontweight='bold')
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/matriz_origem_destino_usp.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV da matriz
    csv_path = f'{OUTPUT_DIR}/../matriz_origem_destino_usp.csv'
    df_matriz.to_csv(csv_path, encoding='utf-8')
    print(f"✅ Matriz salva: {csv_path}")
    
    return df_matriz

def principais_destinos_por_estacao():
    """Para cada estação USP, identifica os principais destinos"""
    print("\n" + "="*80)
    print("  PRINCIPAIS DESTINOS POR ESTAÇÃO")
    print("="*80)
    
    # 17 estacoes USP (PKs internos)
    usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
    estacoes_usp = Station.objects.filter(id__in=usp_pks).order_by('station_id')
    
    # Selecionar top 5 estações para análise detalhada
    dados_estacoes = []
    for estacao in estacoes_usp:
        total = Trip.objects.filter(initial_station=estacao).count()
        dados_estacoes.append({'estacao': estacao, 'total': total})
    
    top5_estacoes = sorted(dados_estacoes, key=lambda x: x['total'], reverse=True)[:5]
    
    print(f"\n📊 Analisando destinos das top 5 estações:")
    
    # Criar subplots
    fig, axes = plt.subplots(5, 1, figsize=(14, 16))
    
    for idx, data in enumerate(top5_estacoes):
        estacao = data['estacao']
        
        # Contar destinos
        destinos_dict = defaultdict(int)
        
        viagens = Trip.objects.filter(initial_station=estacao).select_related('final_station')
        for viagem in viagens:
            if viagem.final_station:
                dest_key = (viagem.final_station.station_id, viagem.final_station.name)
                destinos_dict[dest_key] += 1
        
        # Top 10 destinos
        destinos_sorted = sorted(destinos_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if destinos_sorted:
            dest_labels = [f"{d[0][0]}-{d[0][1][:20]}" for d in destinos_sorted]
            dest_values = [d[1] for d in destinos_sorted]
            
            print(f"\n   {estacao.station_id} - {estacao.name}:")
            for (dest_id, dest_nome), count in destinos_sorted[:5]:
                print(f"      → {dest_id:3d} {dest_nome:30s}: {count:5,} viagens")
            
            # Plotar
            ax = axes[idx]
            colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(dest_values)))
            bars = ax.barh(range(len(dest_values)), dest_values, color=colors, 
                          alpha=0.8, edgecolor='black')
            ax.set_yticks(range(len(dest_labels)))
            ax.set_yticklabels(dest_labels, fontsize=9)
            ax.set_xlabel('Número de Viagens')
            ax.set_title(f"{estacao.station_id} - {estacao.name} (Total saídas: {data['total']:,})",
                        fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Adicionar valores
            for bar, val in zip(bars, dest_values):
                ax.text(bar.get_width() + max(dest_values)*0.01, 
                       bar.get_y() + bar.get_height()/2,
                       f'{val:,}', va='center', fontsize=8)
    
    plt.suptitle('Top 10 Destinos das 5 Estações Mais Movimentadas', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/principais_destinos_top5_estacoes.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()

def main():
    """Função principal"""
    print("\n" + "🚴" * 40)
    print(" " * 20 + "ANÁLISE DE FLUXOS - BIKESCIENCE USP")
    print(" " * 20 + "Script 04: Rotas e Conexões entre Estações")
    print("🚴" * 40)
    
    try:
        analisar_fluxos_principais()
        fluxos_internos_externos()
        matriz_origem_destino_usp()
        principais_destinos_por_estacao()
        
        print("\n" + "=" * 80)
        print("  ✅ ANÁLISE DE FLUXOS CONCLUÍDA COM SUCESSO!")
        print(f"  📁 Gráficos salvos em: {OUTPUT_DIR}/")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
