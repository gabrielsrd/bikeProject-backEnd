#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar TODAS as estatísticas usadas na monografia
Todas as informações na monografia devem vir deste arquivo (verificável)

Autor: Sistema automatizado
Data: 2025-11-10
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json

# Conectar ao banco de dados
DB_PATH = '../db.sqlite3'
conn = sqlite3.connect(DB_PATH)

print("="*80)
print("GERANDO ESTATÍSTICAS COMPLETAS PARA A MONOGRAFIA")
print("="*80)
print()

# ==============================================================================
# 1. PERÍODO DOS DADOS
# ==============================================================================
print("1. PERÍODO DOS DADOS")
print("-" * 80)

query_periodo = """
SELECT 
    MIN(start_time) as primeira_viagem,
    MAX(start_time) as ultima_viagem,
    COUNT(*) as total_viagens_db
FROM ciclovias_trip
"""
df_periodo = pd.read_sql_query(query_periodo, conn)
primeira_viagem = pd.to_datetime(df_periodo['primeira_viagem'].iloc[0])
ultima_viagem = pd.to_datetime(df_periodo['ultima_viagem'].iloc[0])
total_viagens_db = df_periodo['total_viagens_db'].iloc[0]

print(f"Primeira viagem: {primeira_viagem.strftime('%d/%m/%Y')}")
print(f"Última viagem: {ultima_viagem.strftime('%d/%m/%Y')}")
print(f"Total de viagens no DB: {total_viagens_db:,}")
print()

# ==============================================================================
# 2. ESTAÇÕES USP
# ==============================================================================
print("2. ESTAÇÕES USP")
print("-" * 80)

# IDs reais das estações USP no banco de dados
# Estações com códigos Tembici 240-260 (exceto 24 e 25 que não são USP)
# Obtidos pela busca completa no banco de dados
usp_station_ids = [5, 16, 22, 30, 32, 38, 43, 45, 68, 134, 142, 149, 169, 176, 202, 218, 231, 237, 241, 251]

query_estacoes_usp = f"""
SELECT 
    station_id,
    name,
    COUNT(*) as total_viagens
FROM (
    SELECT initial_station_id as station_id, initial_station_name as name
    FROM ciclovias_trip
    WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
    UNION ALL
    SELECT final_station_id as station_id, final_station_name as name
    FROM ciclovias_trip
    WHERE final_station_id IN ({','.join(map(str, usp_station_ids))})
) as all_trips
GROUP BY station_id, name
ORDER BY total_viagens DESC
"""
df_estacoes_usp = pd.read_sql_query(query_estacoes_usp, conn)

print(f"Total de estações USP: {len(df_estacoes_usp)}")
print(f"Total de viagens envolvendo USP: {df_estacoes_usp['total_viagens'].sum():,}")
print()
print("Ranking de estações USP:")
for idx, row in df_estacoes_usp.iterrows():
    print(f"  {idx+1}. ID {row['station_id']} - {row['name']}: {row['total_viagens']:,} viagens")
print()

# ==============================================================================
# 3. VIAGENS INTERNAS vs EXTERNAS
# ==============================================================================
print("3. VIAGENS INTERNAS vs EXTERNAS")
print("-" * 80)

query_viagens_internas = f"""
SELECT 
    COUNT(*) as viagens_internas
FROM ciclovias_trip
WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
  AND final_station_id IN ({','.join(map(str, usp_station_ids))})
"""
viagens_internas = pd.read_sql_query(query_viagens_internas, conn)['viagens_internas'].iloc[0]

query_viagens_total_usp = f"""
SELECT COUNT(*) as total_usp
FROM ciclovias_trip
WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
   OR final_station_id IN ({','.join(map(str, usp_station_ids))})
"""
total_viagens_usp = pd.read_sql_query(query_viagens_total_usp, conn)['total_usp'].iloc[0]

viagens_externas = total_viagens_usp - viagens_internas
percentual_internas = (viagens_internas / total_viagens_usp) * 100
percentual_externas = (viagens_externas / total_viagens_usp) * 100

print(f"Viagens internas (USP→USP): {viagens_internas:,} ({percentual_internas:.1f}%)")
print(f"Viagens externas (USP↔Cidade): {viagens_externas:,} ({percentual_externas:.1f}%)")
print(f"Total viagens USP: {total_viagens_usp:,}")
print()

# ==============================================================================
# 4. TOP 5 ESTAÇÕES
# ==============================================================================
print("4. TOP 5 ESTAÇÕES")
print("-" * 80)

top5_estacoes = df_estacoes_usp.head(5)
for idx, row in top5_estacoes.iterrows():
    percentual = (row['total_viagens'] / df_estacoes_usp['total_viagens'].sum()) * 100
    print(f"{idx+1}. ID {row['station_id']} - {row['name']}")
    print(f"   Viagens: {row['total_viagens']:,} ({percentual:.1f}% do total USP)")
print()

# ==============================================================================
# 5. PADRÕES TEMPORAIS - HORA
# ==============================================================================
print("5. PADRÕES TEMPORAIS - HORA DO DIA")
print("-" * 80)

query_hora = f"""
SELECT 
    start_hour as hora,
    COUNT(*) as viagens
FROM ciclovias_trip
WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
   OR final_station_id IN ({','.join(map(str, usp_station_ids))})
GROUP BY hora
ORDER BY viagens DESC
"""
df_hora = pd.read_sql_query(query_hora, conn)
hora_pico = df_hora.iloc[0]

print(f"Horário de pico: {hora_pico['hora']:02d}h com {hora_pico['viagens']:,} viagens")
print(f"Percentual no pico: {(hora_pico['viagens'] / total_viagens_usp * 100):.1f}%")
print()

# ==============================================================================
# 6. PADRÕES TEMPORAIS - DIA DA SEMANA
# ==============================================================================
print("6. PADRÕES TEMPORAIS - DIA DA SEMANA")
print("-" * 80)

query_dia_semana = f"""
SELECT 
    CASE start_day
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Segunda'
        WHEN 2 THEN 'Terça'
        WHEN 3 THEN 'Quarta'
        WHEN 4 THEN 'Quinta'
        WHEN 5 THEN 'Sexta'
        WHEN 6 THEN 'Sábado'
    END as dia_semana,
    start_day as dia_num,
    COUNT(*) as viagens
FROM ciclovias_trip
WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
   OR final_station_id IN ({','.join(map(str, usp_station_ids))})
GROUP BY dia_num
ORDER BY dia_num
"""
df_dia_semana = pd.read_sql_query(query_dia_semana, conn)

# Calcular dias úteis (segunda a sexta = 1-5)
viagens_dias_uteis = df_dia_semana[df_dia_semana['dia_num'].between(1, 5)]['viagens'].sum()
viagens_fins_semana = df_dia_semana[df_dia_semana['dia_num'].isin([0, 6])]['viagens'].sum()
percentual_dias_uteis = (viagens_dias_uteis / total_viagens_usp) * 100

print(f"Viagens em dias úteis (seg-sex): {viagens_dias_uteis:,} ({percentual_dias_uteis:.1f}%)")
print(f"Viagens em fins de semana: {viagens_fins_semana:,} ({100-percentual_dias_uteis:.1f}%)")
print()

# ==============================================================================
# 7. PADRÕES TEMPORAIS - MÊS
# ==============================================================================
print("7. PADRÕES TEMPORAIS - MÊS")
print("-" * 80)

query_mes = f"""
SELECT 
    strftime('%Y-%m', start_time) as mes,
    COUNT(*) as viagens
FROM ciclovias_trip
WHERE initial_station_id IN ({','.join(map(str, usp_station_ids))})
   OR final_station_id IN ({','.join(map(str, usp_station_ids))})
GROUP BY mes
ORDER BY viagens DESC
"""
df_mes = pd.read_sql_query(query_mes, conn)

# Meses letivos: março-junho (3-6) e agosto-novembro (8-11)
df_mes['mes_num'] = pd.to_datetime(df_mes['mes']).dt.month
meses_letivos = df_mes[df_mes['mes_num'].isin([3,4,5,6,8,9,10,11])]['viagens'].sum()
percentual_letivo = (meses_letivos / total_viagens_usp) * 100

print(f"Viagens em período letivo: {meses_letivos:,} ({percentual_letivo:.1f}%)")
print(f"Mês de pico: {df_mes.iloc[0]['mes']} com {df_mes.iloc[0]['viagens']:,} viagens")
print()

# ==============================================================================
# 8. TOP ROTAS
# ==============================================================================
print("8. TOP 20 ROTAS (ORIGEM → DESTINO)")
print("-" * 80)

query_rotas = f"""
SELECT 
    initial_station_id as start_station_id,
    initial_station_name as start_station_name,
    final_station_id as end_station_id,
    final_station_name as end_station_name,
    COUNT(*) as viagens
FROM ciclovias_trip
WHERE (initial_station_id IN ({','.join(map(str, usp_station_ids))})
   OR final_station_id IN ({','.join(map(str, usp_station_ids))}))
  AND initial_station_id != final_station_id
GROUP BY initial_station_id, final_station_id
ORDER BY viagens DESC
LIMIT 20
"""
df_rotas = pd.read_sql_query(query_rotas, conn)

for idx, row in df_rotas.head(10).iterrows():
    print(f"{idx+1}. {row['start_station_name']} → {row['end_station_name']}: {row['viagens']:,} viagens")
print()

# ==============================================================================
# 9. SALVAR TODAS AS ESTATÍSTICAS EM JSON
# ==============================================================================
print("9. SALVANDO ESTATÍSTICAS EM JSON")
print("-" * 80)

estatisticas = {
    "metadata": {
        "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script": "GERAR_ESTATISTICAS_COMPLETAS.py",
        "database": DB_PATH
    },
    "periodo": {
        "primeira_viagem": primeira_viagem.strftime("%d/%m/%Y"),
        "ultima_viagem": ultima_viagem.strftime("%d/%m/%Y"),
        "primeira_viagem_iso": primeira_viagem.strftime("%Y-%m-%d"),
        "ultima_viagem_iso": ultima_viagem.strftime("%Y-%m-%d"),
        "anos": round((ultima_viagem - primeira_viagem).days / 365.25, 1)
    },
    "geral": {
        "total_viagens_db": int(total_viagens_db),
        "total_viagens_usp": int(total_viagens_usp),
        "total_estacoes_usp": int(len(df_estacoes_usp)),
        "percentual_viagens_usp": round(total_viagens_usp / total_viagens_db * 100, 2)
    },
    "viagens_tipo": {
        "internas": int(viagens_internas),
        "externas": int(viagens_externas),
        "percentual_internas": round(percentual_internas, 1),
        "percentual_externas": round(percentual_externas, 1)
    },
    "estacoes_ranking": [
        {
            "posicao": idx + 1,
            "station_id": int(row['station_id']),
            "nome": row['name'],
            "viagens": int(row['total_viagens']),
            "percentual": round(row['total_viagens'] / df_estacoes_usp['total_viagens'].sum() * 100, 1)
        }
        for idx, row in df_estacoes_usp.iterrows()
    ],
    "temporal_hora": {
        "hora_pico": int(hora_pico['hora']),
        "viagens_hora_pico": int(hora_pico['viagens']),
        "percentual_hora_pico": round(hora_pico['viagens'] / total_viagens_usp * 100, 1),
        "distribuicao": [
            {"hora": int(row['hora']), "viagens": int(row['viagens'])}
            for _, row in df_hora.iterrows()
        ]
    },
    "temporal_semana": {
        "viagens_dias_uteis": int(viagens_dias_uteis),
        "viagens_fins_semana": int(viagens_fins_semana),
        "percentual_dias_uteis": round(percentual_dias_uteis, 1),
        "percentual_fins_semana": round(100 - percentual_dias_uteis, 1),
        "distribuicao": [
            {"dia": row['dia_semana'], "viagens": int(row['viagens'])}
            for _, row in df_dia_semana.iterrows()
        ]
    },
    "temporal_mes": {
        "viagens_periodo_letivo": int(meses_letivos),
        "percentual_periodo_letivo": round(percentual_letivo, 1),
        "mes_pico": df_mes.iloc[0]['mes'],
        "viagens_mes_pico": int(df_mes.iloc[0]['viagens']),
        "distribuicao": [
            {"mes": row['mes'], "viagens": int(row['viagens'])}
            for _, row in df_mes.iterrows()
        ]
    },
    "rotas_top20": [
        {
            "posicao": idx + 1,
            "origem_id": int(row['start_station_id']),
            "origem_nome": row['start_station_name'],
            "destino_id": int(row['end_station_id']),
            "destino_nome": row['end_station_name'],
            "viagens": int(row['viagens'])
        }
        for idx, row in df_rotas.iterrows()
    ]
}

# Salvar JSON
output_json = 'resultados/estatisticas_monografia_completas.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(estatisticas, f, indent=2, ensure_ascii=False)

print(f"✅ Estatísticas salvas em: {output_json}")
print()

# ==============================================================================
# 10. GERAR ARQUIVO LATEX COM COMANDOS
# ==============================================================================
print("10. GERANDO ARQUIVO LATEX")
print("-" * 80)

latex_content = f"""% Estatísticas Verificáveis da Monografia
% Gerado automaticamente em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
% Fonte: {DB_PATH}
% Script: GERAR_ESTATISTICAS_COMPLETAS.py
%
% IMPORTANTE: Todas as estatísticas na monografia devem vir deste arquivo
% Para verificar/atualizar, execute: python3 GERAR_ESTATISTICAS_COMPLETAS.py

% ====== PERÍODO DOS DADOS ======
% Primeira viagem: {primeira_viagem.strftime("%d/%m/%Y")}
% Última viagem: {ultima_viagem.strftime("%d/%m/%Y")}
% Anos de dados: {round((ultima_viagem - primeira_viagem).days / 365.25, 1)}

% ====== GERAL ======
% Total de viagens no DB: {total_viagens_db:,}
% Total de viagens USP: {total_viagens_usp:,}
% Total de estações USP: {len(df_estacoes_usp)}
% Percentual viagens USP: {round(total_viagens_usp / total_viagens_db * 100, 2)}%

% ====== VIAGENS INTERNAS vs EXTERNAS ======
% Viagens internas (USP→USP): {viagens_internas:,} ({percentual_internas:.1f}%)
% Viagens externas (USP↔Cidade): {viagens_externas:,} ({percentual_externas:.1f}%)

% ====== TOP 5 ESTAÇÕES ======
"""

for idx, row in top5_estacoes.iterrows():
    percentual = (row['total_viagens'] / df_estacoes_usp['total_viagens'].sum()) * 100
    latex_content += f"% {idx+1}. ID {row['station_id']} - {row['name']}: {row['total_viagens']:,} ({percentual:.1f}%)\n"

latex_content += f"""
% ====== PADRÕES TEMPORAIS ======
% Hora de pico: {hora_pico['hora']:02d}h com {hora_pico['viagens']:,} viagens ({hora_pico['viagens'] / total_viagens_usp * 100:.1f}%)
% Dias úteis: {viagens_dias_uteis:,} ({percentual_dias_uteis:.1f}%)
% Fins de semana: {viagens_fins_semana:,} ({100-percentual_dias_uteis:.1f}%)
% Período letivo: {meses_letivos:,} ({percentual_letivo:.1f}%)

% ====== TOP 3 ROTAS ======
"""

for idx, row in df_rotas.head(3).iterrows():
    latex_content += f"% {idx+1}. {row['start_station_name']} → {row['end_station_name']}: {row['viagens']:,} viagens\n"

output_latex = 'resultados/estatisticas_verificaveis.tex'
with open(output_latex, 'w', encoding='utf-8') as f:
    f.write(latex_content)

print(f"✅ Arquivo LaTeX salvo em: {output_latex}")
print()

# ==============================================================================
# 11. GERAR RESUMO TEXTO PARA A MONOGRAFIA
# ==============================================================================
print("11. GERANDO RESUMO PARA A MONOGRAFIA")
print("-" * 80)

resumo = f"""
RESUMO DAS ESTATÍSTICAS PARA A MONOGRAFIA
==========================================

PERÍODO: {primeira_viagem.strftime("%d/%m/%Y")} a {ultima_viagem.strftime("%d/%m/%Y")} ({round((ultima_viagem - primeira_viagem).days / 365.25, 1)} anos)

DADOS GERAIS:
- Total de viagens no sistema: {total_viagens_db:,}
- Total de viagens USP: {total_viagens_usp:,} ({round(total_viagens_usp / total_viagens_db * 100, 2)}% do total)
- Total de estações USP: {len(df_estacoes_usp)}

VIAGENS INTERNAS vs EXTERNAS:
- Internas (USP→USP): {viagens_internas:,} ({percentual_internas:.1f}%)
- Externas (USP↔Cidade): {viagens_externas:,} ({percentual_externas:.1f}%)

TOP 5 ESTAÇÕES:
"""

for idx, row in top5_estacoes.iterrows():
    percentual = (row['total_viagens'] / df_estacoes_usp['total_viagens'].sum()) * 100
    resumo += f"{idx+1}. ID {row['station_id']} - {row['name']}: {row['total_viagens']:,} ({percentual:.1f}%)\n"

resumo += f"""
PADRÕES TEMPORAIS:
- Hora de pico: {hora_pico['hora']:02d}h com {hora_pico['viagens']:,} viagens
- Dias úteis: {percentual_dias_uteis:.1f}% | Fins de semana: {100-percentual_dias_uteis:.1f}%
- Período letivo: {percentual_letivo:.1f}%

TOP 3 ROTAS:
"""

for idx, row in df_rotas.head(3).iterrows():
    resumo += f"{idx+1}. {row['start_station_name']} → {row['end_station_name']}: {row['viagens']:,}\n"

output_resumo = 'resultados/RESUMO_ESTATISTICAS.txt'
with open(output_resumo, 'w', encoding='utf-8') as f:
    f.write(resumo)

print(resumo)
print()
print(f"✅ Resumo salvo em: {output_resumo}")

# Fechar conexão
conn.close()

print()
print("="*80)
print("✅ GERAÇÃO DE ESTATÍSTICAS CONCLUÍDA!")
print("="*80)
print()
print("Arquivos gerados:")
print(f"  1. {output_json} (dados completos em JSON)")
print(f"  2. {output_latex} (comentários para LaTeX)")
print(f"  3. {output_resumo} (resumo em texto)")
print()
print("Para atualizar a monografia, use os valores destes arquivos.")
print()
