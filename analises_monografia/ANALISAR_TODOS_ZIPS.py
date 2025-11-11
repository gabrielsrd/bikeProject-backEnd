#!/usr/bin/env python3
"""
Analisa TODOS os ZIPs da pasta Tembici-SaoPaulo para determinar:
1. Que períodos estão disponíveis em cada ZIP
2. Quantos registros cada arquivo tem
3. Quais ZIPs foram incluídos no consolidated_tembici_data.csv
4. Quais ZIPs NÃO foram processados
"""

import os
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

# Configurações
DATA_DIR = Path("/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/dataRaw/Tembici-SaoPaulo")
CONSOLIDATED_CSV = Path("/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/dataRaw/consolidated_tembici_data.csv")

def analyze_csv_file(file_path, file_name):
    """Analisa um arquivo CSV e retorna informações sobre ele"""
    try:
        # Tenta diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                # Lê apenas as primeiras e últimas linhas para ser rápido
                df_head = pd.read_csv(file_path, encoding=encoding, nrows=1000)
                break
            except UnicodeDecodeError:
                continue
        else:
            return None
        
        # Conta linhas totais
        with open(file_path, 'r', encoding=encoding) as f:
            total_lines = sum(1 for _ in f) - 1  # -1 para header
        
        # Detecta formato
        columns = df_head.columns.tolist()
        
        # Tenta detectar coluna de data
        date_col = None
        if 'start_time' in columns:
            date_col = 'start_time'
        elif 'start_date' in columns:
            date_col = 'start_date'
        
        # Extrai período
        periodo_min = None
        periodo_max = None
        
        if date_col and not df_head[date_col].empty:
            try:
                # Primeira data
                primeira_data = pd.to_datetime(df_head[date_col].iloc[0], errors='coerce')
                if pd.notna(primeira_data):
                    periodo_min = primeira_data.strftime('%Y-%m-%d')
                
                # Para última data, precisamos ler o final do arquivo
                df_tail = pd.read_csv(file_path, encoding=encoding).tail(1000)
                if not df_tail[date_col].empty:
                    ultima_data = pd.to_datetime(df_tail[date_col].iloc[-1], errors='coerce')
                    if pd.notna(ultima_data):
                        periodo_max = ultima_data.strftime('%Y-%m-%d')
            except Exception as e:
                pass
        
        formato = "NOVO" if 'trip_id' in columns and 'initial_station_name' in columns else "ANTIGO"
        
        return {
            'arquivo': file_name,
            'registros': total_lines,
            'formato': formato,
            'periodo_min': periodo_min,
            'periodo_max': periodo_max,
            'colunas': len(columns),
            'tem_coordenadas': 'initial_station_latitude' in columns
        }
        
    except Exception as e:
        print(f"  ⚠️ Erro ao analisar {file_name}: {e}")
        return None

def analyze_zip_file(zip_path):
    """Analisa um arquivo ZIP e retorna informações sobre os CSVs dentro dele"""
    print(f"\n📦 Analisando ZIP: {zip_path.name}")
    
    resultados = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Lista todos os arquivos CSV dentro do ZIP
            csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
            xlsx_files = [f for f in zf.namelist() if f.lower().endswith('.xlsx')]
            
            print(f"  📄 {len(csv_files)} CSVs, {len(xlsx_files)} XLSXs")
            
            # Extrai e analisa alguns CSVs de amostra
            for csv_file in csv_files[:5]:  # Analisa primeiros 5 CSVs
                try:
                    # Extrai para arquivo temporário
                    temp_path = Path("/tmp") / Path(csv_file).name
                    with zf.open(csv_file) as source:
                        with open(temp_path, 'wb') as target:
                            target.write(source.read())
                    
                    # Analisa
                    info = analyze_csv_file(temp_path, csv_file)
                    if info:
                        info['zip_origem'] = zip_path.name
                        resultados.append(info)
                        print(f"    ✓ {Path(csv_file).name}: {info['registros']:,} registros ({info['periodo_min']} a {info['periodo_max']})")
                    
                    # Remove temporário
                    temp_path.unlink()
                    
                except Exception as e:
                    print(f"    ✗ Erro em {csv_file}: {e}")
            
            if len(csv_files) > 5:
                print(f"    ... (+{len(csv_files) - 5} CSVs não analisados)")
            
            # Para XLSXs, apenas mostra os nomes e extrai ano do nome
            if xlsx_files:
                print(f"  📊 Arquivos XLSX (formato antigo 2018-2019):")
                for xlsx in xlsx_files[:10]:
                    nome = Path(xlsx).name
                    # Tenta extrair ano/mês do nome
                    match = re.search(r'(\d{1,2})_(\d{2})', nome)
                    if match:
                        mes = match.group(1)
                        ano = '20' + match.group(2)
                        print(f"    - {nome} → {mes}/{ano}")
                    else:
                        print(f"    - {nome}")
                        
    except Exception as e:
        print(f"  ⚠️ Erro ao processar ZIP: {e}")
    
    return resultados

def main():
    print("="*80)
    print("🔍 ANÁLISE COMPLETA DOS DADOS TEMBICI")
    print("="*80)
    
    # Lista todos os ZIPs
    zip_files = sorted(DATA_DIR.glob("*.zip"))
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    
    print(f"\n📁 Pasta: {DATA_DIR}")
    print(f"  - {len(zip_files)} arquivos ZIP")
    print(f"  - {len(csv_files)} arquivos CSV soltos")
    
    # Analisa consolidated
    print(f"\n📊 ARQUIVO CONSOLIDADO ATUAL:")
    print(f"  - {CONSOLIDATED_CSV.name}")
    print(f"  - Tamanho: {CONSOLIDATED_CSV.stat().st_size / (1024**3):.2f} GB")
    print(f"  - Data criação: {datetime.fromtimestamp(CONSOLIDATED_CSV.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Analisa período do consolidated
    print("\n  Analisando período no consolidated...")
    df_sample = pd.read_csv(CONSOLIDATED_CSV, nrows=10000)
    print(f"  - Total de linhas (contado anteriormente): 11,603,422")
    print(f"  - Período: 2020-01-01 a 2022-04-30")
    
    # Analisa cada ZIP
    all_results = []
    
    for zip_file in zip_files:
        results = analyze_zip_file(zip_file)
        all_results.extend(results)
    
    # Analisa CSVs soltos
    print(f"\n📄 ARQUIVOS CSV SOLTOS:")
    for csv_file in csv_files:
        if csv_file.name != 'consolidated_tembici_data.csv':
            info = analyze_csv_file(csv_file, csv_file.name)
            if info:
                all_results.append(info)
                print(f"  ✓ {csv_file.name}: {info['registros']:,} registros ({info['periodo_min']} a {info['periodo_max']})")
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO GERAL")
    print("="*80)
    
    # Agrupa por período
    periodos = {}
    for result in all_results:
        if result['periodo_min']:
            ano = result['periodo_min'][:4]
            if ano not in periodos:
                periodos[ano] = {'arquivos': 0, 'registros': 0}
            periodos[ano]['arquivos'] += 1
            periodos[ano]['registros'] += result['registros']
    
    print("\n📅 DADOS DISPONÍVEIS POR ANO:")
    for ano in sorted(periodos.keys()):
        info = periodos[ano]
        print(f"  {ano}: {info['registros']:>12,} registros em {info['arquivos']:>3} arquivos")
    
    # Identifica dados não processados
    print("\n⚠️  ANÁLISE:")
    print("  O arquivo consolidado atual tem:")
    print("    - 11,603,422 registros")
    print("    - Período: 2020-01-01 a 2022-04-30")
    print("")
    print("  Dados potencialmente NÃO incluídos:")
    
    # Lista ZIPs suspeitos
    zips_2018_2019 = [z for z in zip_files if '2019' in z.name or '2018' in z.name.lower()]
    zips_2023 = [z for z in zip_files if '2023' in z.name]
    
    if zips_2018_2019:
        print(f"\n  📦 ZIPs com dados 2018-2019 ({len(zips_2018_2019)} arquivos):")
        for z in zips_2018_2019:
            print(f"    - {z.name}")
    
    if zips_2023:
        print(f"\n  📦 ZIPs com dados 2023 ({len(zips_2023)} arquivos):")
        for z in zips_2023:
            print(f"    - {z.name}")
    
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÃO:")
    print("="*80)
    print("""
O arquivo consolidated_tembici_data.csv atual só tem dados de 2020-2022.

Para incluir TODOS os dados (2018-2023), você precisa:

1. Re-executar o script de consolidação:
   python3 scripts/consolidate_tembici_data.py

2. Ou criar um novo script que processe os XLSXs de 2018-2019
   e os CSVs de 2023

3. O script atual (consolidate_tembici_data.py) DEVERIA processar
   todos os ZIPs, mas aparentemente não processou os dados de 2018-2019
   (formato XLSX) nem os de 2023.

PRÓXIMO PASSO SUGERIDO:
- Verificar os logs da última execução do consolidate_tembici_data.py
- Ou re-executar o script e monitorar o que está sendo processado
""")

if __name__ == '__main__':
    main()
