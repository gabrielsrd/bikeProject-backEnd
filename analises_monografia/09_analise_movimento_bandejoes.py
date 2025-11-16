#!/usr/bin/env python3
"""
ANÁLISE 4: MOVIMENTO DOS BANDEJÕES (RESTAURANTES UNIVERSITÁRIOS)
================================================================

Objetivo: Analisar o movimento característico nos restaurantes universitários,
especialmente no horário de almoço (11h-14h).

Contexto USP:
- Bandejão Central é um dos principais destinos
- Bandejão da Química e Prefeitura também são importantes
- Horário de pico: 11h30-12h30
- Padrão de ida (11h-13h) e retorno (13h-14h)

Consultas SQL documentadas para verificação do professor.
"""

import os
import sys
import django
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np

# Configurar Django
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db.models import Count, Q, Avg
from ciclovias.models import Trip

# Diretório de saída
OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def print_sql_query(description, queryset):
    """Imprime a query SQL para documentação"""
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")
    print(queryset.query)
    print(f"{'='*80}\n")

# Nomes dos bandejões (variações possíveis)
BANDEJOES = {
    'Central': ['Bandejão Central', 'Central'],
    'Química': ['Bandejão Química', 'Química', 'Quimica'],
    'Prefeitura': ['Bandejão Prefeitura', 'Prefeitura']
}

def encontrar_bandejoes_no_banco():
    """Encontra os nomes exatos dos bandejões no banco"""
    nomes_encontrados = {}
    
    for bandejao, variacoes in BANDEJOES.items():
        for var in variacoes:
            # Verificar se existe
            existe_destino = Trip.objects.filter(final_station_name__icontains=var).exists()
            existe_origem = Trip.objects.filter(initial_station_name__icontains=var).exists()
            
            if existe_destino or existe_origem:
                # Pegar o nome exato mais usado
                nome_exato = Trip.objects.filter(
                    Q(final_station_name__icontains=var) | Q(initial_station_name__icontains=var)
                ).values('final_station_name').annotate(
                    total=Count('id')
                ).order_by('-total').first()
                
                if nome_exato:
                    nomes_encontrados[bandejao] = nome_exato['final_station_name']
                    break
    
    return nomes_encontrados

def analise_movimento_bandejoes():
    """
    Análise principal: Padrões de uso dos restaurantes universitários
    """
    
    print("="*80)
    print("ANÁLISE 4: MOVIMENTO DOS BANDEJÕES (RESTAURANTES UNIVERSITÁRIOS)")
    print("="*80)
    
    # Encontrar nomes exatos dos bandejões
    print("\n🔍 Procurando bandejões no banco de dados...")
    bandejoes_db = encontrar_bandejoes_no_banco()
    
    print(f"\n✅ Bandejões encontrados:")
    for nome, nome_db in bandejoes_db.items():
        print(f"   {nome}: '{nome_db}'")
    
    if not bandejoes_db:
        print("\n❌ Nenhum bandejão encontrado! Listando estações mais usadas...")
        
        top_estacoes = Trip.objects.values('final_station_name').annotate(
            total=Count('id')
        ).order_by('-total')[:20]
        
        print("\nTop 20 estações de destino:")
        for idx, est in enumerate(top_estacoes, 1):
            print(f"   {idx:2d}. {est['final_station_name']:<50} {est['total']:>8,} chegadas")
        
        # Tentar ajustar automaticamente
        print("\n🔧 Ajustando para buscar qualquer estação com 'Bandejão' ou 'Central'...")
        bandejoes_db = {}
        
    todos_bandejoes = list(bandejoes_db.values()) if bandejoes_db else []
    
    # Se ainda não encontrou, usar busca genérica
    if not todos_bandejoes:
        print("\n⚠️  Usando busca genérica por 'Central', 'Química' ou 'Prefeitura'...")
        
        viagens_genericas = Trip.objects.filter(
            Q(final_station_name__icontains='Central') |
            Q(final_station_name__icontains='Química') |
            Q(final_station_name__icontains='Quimica') |
            Q(final_station_name__icontains='Prefeitura')
        ).values('final_station_name').annotate(
            total=Count('id')
        ).order_by('-total')
        
        for item in viagens_genericas:
            print(f"   Encontrado: {item['final_station_name']} ({item['total']:,} viagens)")
            todos_bandejoes.append(item['final_station_name'])
    
    if not todos_bandejoes:
        print("\n❌ Não foi possível encontrar bandejões. Encerrando análise.")
        return {}
    
    # =================================================================
    # CONSULTA 1: Viagens CHEGANDO nos bandejões (destino)
    # =================================================================
    viagens_chegada = Trip.objects.filter(
        final_station_name__in=todos_bandejoes
    ).values('final_station_name').annotate(
        total=Count('id'),
        duracao_media=Avg('duration_seconds')
    ).order_by('-total')
    
    print_sql_query(
        "Viagens CHEGANDO nos bandejões",
        viagens_chegada
    )
    
    # =================================================================
    # CONSULTA 2: Viagens SAINDO dos bandejões (origem)
    # =================================================================
    viagens_saida = Trip.objects.filter(
        initial_station_name__in=todos_bandejoes
    ).values('initial_station_name').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print_sql_query(
        "Viagens SAINDO dos bandejões",
        viagens_saida
    )
    
    # =================================================================
    # CONSULTA 3: Distribuição horária de CHEGADAS nos bandejões
    # =================================================================
    chegadas_por_hora = Trip.objects.filter(
        final_station_name__in=todos_bandejoes
    ).values('start_hour').annotate(
        total=Count('id')
    ).order_by('start_hour')
    
    print_sql_query(
        "Chegadas nos bandejões por hora",
        chegadas_por_hora
    )
    
    # =================================================================
    # CONSULTA 4: Principais ORIGENS para os bandejões (horário de almoço)
    # =================================================================
    origens_almoco = Trip.objects.filter(
        final_station_name__in=todos_bandejoes,
        start_hour__gte=11,
        start_hour__lt=14
    ).values('initial_station_name').annotate(
        total=Count('id')
    ).order_by('-total')[:15]
    
    print_sql_query(
        "Top 15 origens para bandejões no horário de almoço (11h-14h)",
        origens_almoco
    )
    
    # =================================================================
    # ESTATÍSTICAS
    # =================================================================
    df_chegada = pd.DataFrame(list(viagens_chegada))
    df_saida = pd.DataFrame(list(viagens_saida))
    
    total_chegadas = df_chegada['total'].sum() if not df_chegada.empty else 0
    total_saidas = df_saida['total'].sum() if not df_saida.empty else 0
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de chegadas nos bandejões: {int(total_chegadas):,}")
    print(f"   Total de saídas dos bandejões: {int(total_saidas):,}")
    print(f"   Saldo (chegadas - saídas): {int(total_chegadas - total_saidas):,}")
    
    print(f"\n🍽️  CHEGADAS POR BANDEJÃO:")
    if not df_chegada.empty:
        for _, row in df_chegada.iterrows():
            duracao_min = row['duracao_media'] / 60 if pd.notna(row['duracao_media']) else 0
            print(f"   {row['final_station_name']:<40} {int(row['total']):>8,} chegadas (duração média: {duracao_min:.1f} min)")
    
    print(f"\n🚴 TOP 15 ORIGENS PARA BANDEJÕES (horário de almoço 11h-14h):")
    for idx, orig in enumerate(origens_almoco, 1):
        print(f"   {idx:2d}. {orig['initial_station_name']:<45} {orig['total']:>6,} viagens")
    
    # =================================================================
    # PREPARAR DADOS PARA GRÁFICOS
    # =================================================================
    horas = np.arange(0, 24)
    chegadas_array = np.zeros(24)
    
    for item in chegadas_por_hora:
        if item['start_hour'] is not None:
            chegadas_array[item['start_hour']] = item['total']
    
    # =================================================================
    # GRÁFICO 1: Chegadas e Saídas por bandejão
    # =================================================================
    if not df_chegada.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bandejoes_nomes = df_chegada['final_station_name'].tolist()
        chegadas_valores = df_chegada['total'].tolist()
        
        # Buscar saídas correspondentes
        saidas_valores = []
        for nome in bandejoes_nomes:
            saida = df_saida[df_saida['initial_station_name'] == nome]['total']
            saidas_valores.append(saida.iloc[0] if not saida.empty else 0)
        
        x = np.arange(len(bandejoes_nomes))
        width = 0.35
        
        ax.bar(x - width/2, chegadas_valores, width,
               label='Chegadas', color='#06A77D', alpha=0.8, edgecolor='black')
        ax.bar(x + width/2, saidas_valores, width,
               label='Saídas', color='#E63946', alpha=0.8, edgecolor='black')
        
        ax.set_title('Movimento dos Bandejões: Chegadas vs Saídas', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Bandejão', fontsize=12)
        ax.set_ylabel('Número de Viagens', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels([n.replace(' ', '\n') for n in bandejoes_nomes], fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        filepath1 = os.path.join(OUTPUT_DIR, 'analise_09_bandejoes_chegadas_saidas.png')
        plt.savefig(filepath1, dpi=300, bbox_inches='tight')
        print(f"\n✅ Gráfico salvo: {filepath1}")
        plt.close()
    
    # =================================================================
    # GRÁFICO 2: Distribuição horária de chegadas
    # =================================================================
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.bar(horas, chegadas_array, color='#F77F00', alpha=0.8, edgecolor='black')
    
    # Destacar horário de almoço
    ax.axvspan(11, 14, alpha=0.2, color='red', label='Horário de almoço (11h-14h)')
    ax.axvline(x=12, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Pico esperado (12h)')
    
    ax.set_title('Chegadas nos Bandejões por Hora do Dia', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Hora do Dia', fontsize=12)
    ax.set_ylabel('Número de Chegadas', fontsize=12)
    ax.set_xticks(horas)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Anotar valores de pico
    hora_pico = np.argmax(chegadas_array)
    valor_pico = chegadas_array[hora_pico]
    if valor_pico > 0:
        ax.annotate(f'Pico: {int(valor_pico):,} viagens',
                   xy=(hora_pico, valor_pico),
                   xytext=(hora_pico + 1, valor_pico * 1.1),
                   arrowprops=dict(arrowstyle='->', color='black'),
                   fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    filepath2 = os.path.join(OUTPUT_DIR, 'analise_09_bandejoes_horario.png')
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {filepath2}")
    plt.close()
    
    # =================================================================
    # GRÁFICO 3: Top origens para bandejões
    # =================================================================
    if origens_almoco:
        df_origens = pd.DataFrame(list(origens_almoco))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Limitar para top 10 para melhor visualização
        top_10 = df_origens.head(10)
        
        ax.barh(range(len(top_10)), top_10['total'], color='#2E86AB', alpha=0.8, edgecolor='black')
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10['initial_station_name'], fontsize=10)
        ax.invert_yaxis()
        
        ax.set_title('Top 10 Origens para Bandejões (Horário de Almoço 11h-14h)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Número de Viagens', fontsize=12)
        ax.grid(axis='x', alpha=0.3)
        
        # Adicionar valores nas barras
        for i, (idx, row) in enumerate(top_10.iterrows()):
            ax.text(row['total'] + max(top_10['total'])*0.01, i, 
                   f"{int(row['total']):,}", 
                   va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        filepath3 = os.path.join(OUTPUT_DIR, 'analise_09_bandejoes_origens.png')
        plt.savefig(filepath3, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico salvo: {filepath3}")
        plt.close()
    
    # =================================================================
    # SALVAR DADOS TABULARES
    # =================================================================
    csv_path1 = os.path.join(OUTPUT_DIR, 'analise_09_bandejoes_estatisticas.csv')
    if not df_chegada.empty:
        df_chegada.to_csv(csv_path1, index=False)
        print(f"\n✅ Dados salvos: {csv_path1}")
    
    csv_path2 = os.path.join(OUTPUT_DIR, 'analise_09_bandejoes_horario.csv')
    df_horario = pd.DataFrame({
        'hora': horas,
        'chegadas': chegadas_array.astype(int)
    })
    df_horario.to_csv(csv_path2, index=False)
    print(f"✅ Dados salvos: {csv_path2}")
    
    print("\n" + "="*80)
    print("✅ ANÁLISE 4 CONCLUÍDA!")
    print("="*80)
    
    return {
        'total_chegadas': int(total_chegadas),
        'total_saidas': int(total_saidas),
        'hora_pico': int(hora_pico) if 'hora_pico' in locals() else 12
    }

if __name__ == '__main__':
    resultado = analise_movimento_bandejoes()
    if resultado:
        print(f"\n📊 Resumo: {resultado['total_chegadas']:,} chegadas nos bandejões")
