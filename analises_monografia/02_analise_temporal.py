#!/usr/bin/env python3
"""
Script 02: Análise Temporal das Viagens
========================================

Este script analisa padrões temporais das viagens USP:
- Distribuição por hora do dia
- Distribuição por dia da semana
- Distribuição por mês
- Comparação entre dias úteis e fins de semana
- Impacto da pandemia COVID-19

Gera gráficos para inclusão na monografia.

Autor: Gabriel da Silva Alves
Data: Novembro 2025
Projeto: TCC - Análise de viagens de bicicletas compartilhadas na USP
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Count, Q

# Configuração de estilo para gráficos
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Criar diretório de saída
OUTPUT_DIR = 'analises_monografia/resultados/graficos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def obter_viagens_usp():
    """Retorna queryset de viagens USP"""
    estacoes_usp = Station.objects.filter(station_id__gte=242, station_id__lte=260)
    return Trip.objects.filter(
        Q(initial_station__in=estacoes_usp) | Q(final_station__in=estacoes_usp)
    )

def analise_por_hora():
    """Analisa distribuição de viagens por hora do dia"""
    print("\n" + "="*80)
    print("  ANÁLISE POR HORA DO DIA")
    print("="*80)
    
    viagens_usp = obter_viagens_usp()
    
    # Contar viagens por hora
    horas_dict = defaultdict(int)
    for viagem in viagens_usp.values('start_hour'):
        if viagem['start_hour'] is not None:
            horas_dict[viagem['start_hour']] += 1
    
    # Converter para DataFrame
    df = pd.DataFrame([
        {'hora': h, 'viagens': count} 
        for h, count in sorted(horas_dict.items())
    ])
    
    # Estatísticas
    print(f"\n📊 Total de viagens analisadas: {df['viagens'].sum():,}")
    print(f"📊 Hora com mais viagens: {df.loc[df['viagens'].idxmax(), 'hora']}h ({df['viagens'].max():,} viagens)")
    print(f"📊 Hora com menos viagens: {df.loc[df['viagens'].idxmin(), 'hora']}h ({df['viagens'].min():,} viagens)")
    
    # Identificar horários de pico (acima de 80% do máximo)
    limite_pico = df['viagens'].max() * 0.8
    horarios_pico = df[df['viagens'] >= limite_pico]['hora'].tolist()
    print(f"📊 Horários de pico (>80% do máximo): {horarios_pico}")
    
    # Gráfico
    plt.figure(figsize=(14, 6))
    bars = plt.bar(df['hora'], df['viagens'], color='steelblue', alpha=0.8, edgecolor='black')
    
    # Destacar horários de pico
    for i, (hora, viagens) in enumerate(zip(df['hora'], df['viagens'])):
        if hora in horarios_pico:
            bars[i].set_color('coral')
    
    plt.xlabel('Hora do Dia', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Viagens', fontsize=12, fontweight='bold')
    plt.title('Distribuição de Viagens USP por Hora do Dia', fontsize=14, fontweight='bold')
    plt.xticks(range(24))
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Salvar
    filepath = f'{OUTPUT_DIR}/viagens_por_hora.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../viagens_por_hora.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df

def analise_por_dia_semana():
    """Analisa distribuição de viagens por dia da semana"""
    print("\n" + "="*80)
    print("  ANÁLISE POR DIA DA SEMANA")
    print("="*80)
    
    viagens_usp = obter_viagens_usp()
    
    # Contar viagens por dia da semana
    dias_dict = defaultdict(int)
    for viagem in viagens_usp.values('start_day'):
        if viagem['start_day'] is not None:
            dias_dict[viagem['start_day']] += 1
    
    # Nomes dos dias
    dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    df = pd.DataFrame([
        {'dia_num': d, 'dia_nome': dias_nomes[d], 'viagens': dias_dict.get(d, 0)} 
        for d in range(7)
    ])
    
    # Estatísticas
    print(f"\n📊 Total de viagens analisadas: {df['viagens'].sum():,}")
    print(f"📊 Dia com mais viagens: {df.loc[df['viagens'].idxmax(), 'dia_nome']} ({df['viagens'].max():,})")
    print(f"📊 Dia com menos viagens: {df.loc[df['viagens'].idxmin(), 'dia_nome']} ({df['viagens'].min():,})")
    
    # Comparar dias úteis vs fim de semana
    dias_uteis = df[df['dia_num'] < 5]['viagens'].sum()
    fim_semana = df[df['dia_num'] >= 5]['viagens'].sum()
    print(f"\n📊 Dias úteis (Seg-Sex): {dias_uteis:,} viagens ({dias_uteis/(dias_uteis+fim_semana)*100:.1f}%)")
    print(f"📊 Fim de semana (Sáb-Dom): {fim_semana:,} viagens ({fim_semana/(dias_uteis+fim_semana)*100:.1f}%)")
    print(f"📊 Média por dia útil: {dias_uteis/5:,.0f} viagens")
    print(f"📊 Média por dia de fim de semana: {fim_semana/2:,.0f} viagens")
    
    # Gráfico
    plt.figure(figsize=(12, 6))
    colors = ['steelblue' if d < 5 else 'coral' for d in df['dia_num']]
    bars = plt.bar(df['dia_nome'], df['viagens'], color=colors, alpha=0.8, edgecolor='black')
    
    plt.xlabel('Dia da Semana', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Viagens', fontsize=12, fontweight='bold')
    plt.title('Distribuição de Viagens USP por Dia da Semana', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='Dias úteis'),
        Patch(facecolor='coral', alpha=0.8, label='Fim de semana')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/viagens_por_dia_semana.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../viagens_por_dia_semana.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df

def analise_por_mes():
    """Analisa distribuição de viagens por mês"""
    print("\n" + "="*80)
    print("  ANÁLISE POR MÊS")
    print("="*80)
    
    viagens_usp = obter_viagens_usp()
    
    # Contar viagens por mês
    meses_dict = defaultdict(int)
    for viagem in viagens_usp.values('month'):
        if viagem['month'] is not None:
            meses_dict[viagem['month']] += 1
    
    # Nomes dos meses
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    df = pd.DataFrame([
        {'mes_num': m, 'mes_nome': meses_nomes[m-1], 'viagens': meses_dict.get(m, 0)} 
        for m in range(1, 13)
    ])
    
    # Estatísticas
    print(f"\n📊 Total de viagens analisadas: {df['viagens'].sum():,}")
    print(f"📊 Mês com mais viagens: {df.loc[df['viagens'].idxmax(), 'mes_nome']} ({df['viagens'].max():,})")
    print(f"📊 Mês com menos viagens: {df.loc[df['viagens'].idxmin(), 'mes_nome']} ({df['viagens'].min():,})")
    
    # Identificar meses de férias (Jan, Fev, Jul, Dez)
    meses_ferias = [1, 2, 7, 12]
    viagens_ferias = df[df['mes_num'].isin(meses_ferias)]['viagens'].sum()
    viagens_letivo = df[~df['mes_num'].isin(meses_ferias)]['viagens'].sum()
    
    print(f"\n📊 Meses de férias (Jan, Fev, Jul, Dez): {viagens_ferias:,} viagens ({viagens_ferias/df['viagens'].sum()*100:.1f}%)")
    print(f"📊 Período letivo (outros meses): {viagens_letivo:,} viagens ({viagens_letivo/df['viagens'].sum()*100:.1f}%)")
    
    # Gráfico
    plt.figure(figsize=(12, 6))
    colors = ['coral' if m in meses_ferias else 'steelblue' for m in df['mes_num']]
    bars = plt.bar(df['mes_nome'], df['viagens'], color=colors, alpha=0.8, edgecolor='black')
    
    plt.xlabel('Mês', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Viagens', fontsize=12, fontweight='bold')
    plt.title('Distribuição de Viagens USP por Mês (Todos os Anos Agregados)', 
              fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='Período letivo'),
        Patch(facecolor='coral', alpha=0.8, label='Férias')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/viagens_por_mes.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../viagens_por_mes.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df

def analise_por_ano_mes():
    """Analisa evolução temporal das viagens por ano e mês"""
    print("\n" + "="*80)
    print("  ANÁLISE TEMPORAL (ANO x MÊS)")
    print("="*80)
    
    viagens_usp = obter_viagens_usp()
    
    # Agrupar por ano e mês
    dados_temporais = []
    for viagem in viagens_usp.values('start_time'):
        if viagem['start_time']:
            ano = viagem['start_time'].year
            mes = viagem['start_time'].month
            dados_temporais.append({'ano': ano, 'mes': mes})
    
    df = pd.DataFrame(dados_temporais)
    df_agrupado = df.groupby(['ano', 'mes']).size().reset_index(name='viagens')
    df_agrupado['ano_mes'] = df_agrupado['ano'].astype(str) + '-' + df_agrupado['mes'].astype(str).str.zfill(2)
    df_agrupado = df_agrupado.sort_values(['ano', 'mes'])
    
    print(f"\n📊 Total de viagens analisadas: {df_agrupado['viagens'].sum():,}")
    print(f"\n📊 Período com mais viagens: {df_agrupado.loc[df_agrupado['viagens'].idxmax(), 'ano_mes']} ({df_agrupado['viagens'].max():,})")
    print(f"📊 Período com menos viagens: {df_agrupado.loc[df_agrupado['viagens'].idxmin(), 'ano_mes']} ({df_agrupado['viagens'].min():,})")
    
    # Identificar período COVID-19 (2020-2021)
    df_agrupado['periodo'] = 'Normal'
    df_agrupado.loc[df_agrupado['ano'].isin([2020, 2021]), 'periodo'] = 'COVID-19'
    
    viagens_pre_covid = df_agrupado[df_agrupado['ano'] < 2020]['viagens'].sum()
    viagens_covid = df_agrupado[df_agrupado['ano'].isin([2020, 2021])]['viagens'].sum()
    viagens_pos_covid = df_agrupado[df_agrupado['ano'] > 2021]['viagens'].sum()
    
    print(f"\n📊 IMPACTO COVID-19:")
    print(f"   • Pré-pandemia (até 2019): {viagens_pre_covid:,} viagens")
    print(f"   • Durante pandemia (2020-2021): {viagens_covid:,} viagens")
    print(f"   • Pós-pandemia (2022+): {viagens_pos_covid:,} viagens")
    
    # Gráfico
    plt.figure(figsize=(16, 6))
    colors = ['coral' if ano in [2020, 2021] else 'steelblue' 
              for ano in df_agrupado['ano']]
    
    plt.bar(range(len(df_agrupado)), df_agrupado['viagens'], 
            color=colors, alpha=0.8, edgecolor='black', width=0.8)
    
    # Configurar xticks para mostrar apenas alguns labels
    indices = range(0, len(df_agrupado), 3)  # Mostrar a cada 3 meses
    labels = [df_agrupado.iloc[i]['ano_mes'] for i in indices]
    plt.xticks(indices, labels, rotation=45, ha='right')
    
    plt.xlabel('Período (Ano-Mês)', fontsize=12, fontweight='bold')
    plt.ylabel('Número de Viagens', fontsize=12, fontweight='bold')
    plt.title('Evolução Temporal das Viagens USP (2018-2023)', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar linha vertical para marcar início da pandemia
    inicio_covid = df_agrupado[df_agrupado['ano_mes'] == '2020-03'].index[0] if len(df_agrupado[df_agrupado['ano_mes'] == '2020-03']) > 0 else None
    if inicio_covid:
        plt.axvline(x=inicio_covid, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Início COVID-19 (Mar/2020)')
    
    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='Período normal'),
        Patch(facecolor='coral', alpha=0.8, label='COVID-19 (2020-2021)')
    ]
    if inicio_covid:
        plt.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/evolucao_temporal_viagens.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../evolucao_temporal_viagens.csv'
    df_agrupado.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df_agrupado

def comparacao_util_fds_por_hora():
    """Compara padrão de uso entre dias úteis e fim de semana por hora"""
    print("\n" + "="*80)
    print("  COMPARAÇÃO: DIAS ÚTEIS vs FIM DE SEMANA (POR HORA)")
    print("="*80)
    
    viagens_usp = obter_viagens_usp()
    
    # Separar dias úteis e fim de semana
    dias_uteis_dict = defaultdict(int)
    fim_semana_dict = defaultdict(int)
    
    for viagem in viagens_usp.values('start_hour', 'start_day'):
        if viagem['start_hour'] is not None and viagem['start_day'] is not None:
            hora = viagem['start_hour']
            dia = viagem['start_day']
            
            if dia < 5:  # Segunda a sexta (0-4)
                dias_uteis_dict[hora] += 1
            else:  # Sábado e domingo (5-6)
                fim_semana_dict[hora] += 1
    
    # Criar DataFrame
    horas = range(24)
    df = pd.DataFrame({
        'hora': horas,
        'dias_uteis': [dias_uteis_dict.get(h, 0) for h in horas],
        'fim_semana': [fim_semana_dict.get(h, 0) for h in horas]
    })
    
    # Normalizar por número de dias
    df['dias_uteis_media'] = df['dias_uteis'] / 5  # 5 dias úteis
    df['fim_semana_media'] = df['fim_semana'] / 2  # 2 dias de fim de semana
    
    print(f"\n📊 Total viagens dias úteis: {df['dias_uteis'].sum():,}")
    print(f"📊 Total viagens fim de semana: {df['fim_semana'].sum():,}")
    print(f"📊 Média por dia útil: {df['dias_uteis'].sum()/5:,.0f}")
    print(f"📊 Média por dia de fim de semana: {df['fim_semana'].sum()/2:,.0f}")
    
    # Gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Subplot 1: Totais
    width = 0.35
    x = range(24)
    ax1.bar([i - width/2 for i in x], df['dias_uteis'], width, 
            label='Dias úteis', color='steelblue', alpha=0.8, edgecolor='black')
    ax1.bar([i + width/2 for i in x], df['fim_semana'], width, 
            label='Fim de semana', color='coral', alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Hora do Dia', fontweight='bold')
    ax1.set_ylabel('Número de Viagens (Total)', fontweight='bold')
    ax1.set_title('Comparação: Dias Úteis vs Fim de Semana (Totais)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Médias
    ax2.bar([i - width/2 for i in x], df['dias_uteis_media'], width, 
            label='Dias úteis (média)', color='steelblue', alpha=0.8, edgecolor='black')
    ax2.bar([i + width/2 for i in x], df['fim_semana_media'], width, 
            label='Fim de semana (média)', color='coral', alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Hora do Dia', fontweight='bold')
    ax2.set_ylabel('Número de Viagens (Média por dia)', fontweight='bold')
    ax2.set_title('Comparação: Dias Úteis vs Fim de Semana (Médias)', fontweight='bold')
    ax2.set_xticks(x)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    filepath = f'{OUTPUT_DIR}/comparacao_util_fds_hora.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico salvo: {filepath}")
    plt.close()
    
    # Salvar CSV
    csv_path = f'{OUTPUT_DIR}/../comparacao_util_fds_hora.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Dados salvos: {csv_path}")
    
    return df

def main():
    """Função principal"""
    print("\n" + "🚴" * 40)
    print(" " * 20 + "ANÁLISE TEMPORAL - BIKESCIENCE USP")
    print(" " * 20 + "Script 02: Padrões Temporais")
    print("🚴" * 40)
    
    try:
        # Executar análises
        analise_por_hora()
        analise_por_dia_semana()
        analise_por_mes()
        analise_por_ano_mes()
        comparacao_util_fds_por_hora()
        
        print("\n" + "=" * 80)
        print("  ✅ ANÁLISE TEMPORAL CONCLUÍDA COM SUCESSO!")
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
