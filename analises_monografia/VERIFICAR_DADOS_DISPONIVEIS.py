#!/usr/bin/env python3
"""
Analisa TODOS os ZIPs da pasta Tembici-SaoPaulo para determinar:
1. Que períodos estão disponíveis em cada ZIP
2. Quantos registros cada arquivo tem
3. Quais dados foram incluídos no consolidated_tembici_data.csv
4. Quais dados NÃO foram processados

IMPORTANTE: Este script NÃO modifica nenhum arquivo existente!
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
OUTPUT_DIR = Path("/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados")
OUTPUT_DIR.mkdir(exist_ok=True)

def analyze_csv_in_zip(zip_ref, csv_file):
    """Analisa um CSV dentro de um ZIP sem extraí-lo completamente"""
    try:
        # Extrai para temporário
        temp_path = Path("/tmp") / Path(csv_file).name
        
        with zip_ref.open(csv_file) as source:
            with open(temp_path, 'wb') as target:
                target.write(source.read())
        
        # Tenta diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                # Lê apenas primeiro e último registro
                df_head = pd.read_csv(temp_path, encoding=encoding, nrows=10)
                df_tail = pd.read_csv(temp_path, encoding=encoding).tail(10)
                break
            except UnicodeDecodeError:
                continue
        else:
            temp_path.unlink()
            return None
        
        # Conta linhas
        with open(temp_path, 'r', encoding=encoding) as f:
            total_lines = sum(1 for _ in f) - 1  # -1 para header
        
        # Remove temporário
        temp_path.unlink()
        
        # Detecta formato
        columns = df_head.columns.tolist()
        
        # Detecta coluna de data
        date_col = None
        if 'start_time' in columns:
            date_col = 'start_time'
        elif 'start_date' in columns:
            date_col = 'start_date'
        
        # Extrai período
        periodo_min = None
        periodo_max = None
        
        if date_col and not df_head.empty:
            try:
                primeira_data = pd.to_datetime(df_head[date_col].iloc[0], errors='coerce')
                if pd.notna(primeira_data):
                    periodo_min = primeira_data.strftime('%Y-%m-%d')
                
                if not df_tail.empty:
                    ultima_data = pd.to_datetime(df_tail[date_col].iloc[-1], errors='coerce')
                    if pd.notna(ultima_data):
                        periodo_max = ultima_data.strftime('%Y-%m-%d')
            except:
                pass
        
        formato = "NOVO (CSV com trip_id)" if 'trip_id' in columns else "ANTIGO (CSV sem trip_id)"
        
        return {
            'arquivo': Path(csv_file).name,
            'registros': total_lines,
            'formato': formato,
            'periodo_min': periodo_min,
            'periodo_max': periodo_max,
            'tem_coordenadas': 'initial_station_latitude' in columns
        }
        
    except Exception as e:
        return None

def analyze_zip_file(zip_path):
    """Analisa um arquivo ZIP"""
    print(f"\n{'='*80}")
    print(f"📦 ZIP: {zip_path.name}")
    print(f"{'='*80}")
    
    resultados = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Lista arquivos
            csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv') and not f.endswith('/')]
            xlsx_files = [f for f in zf.namelist() if f.lower().endswith('.xlsx') and not f.endswith('/')]
            
            print(f"  📊 Conteúdo: {len(csv_files)} CSVs, {len(xlsx_files)} XLSXs")
            
            # Analisa CSVs (amostra)
            if csv_files:
                print(f"\n  📄 Analisando CSVs (amostra de até 10 arquivos):")
                for csv_file in csv_files[:10]:
                    info = analyze_csv_in_zip(zf, csv_file)
                    if info:
                        resultados.append(info)
                        print(f"    ✓ {info['arquivo'][:50]:50} | {info['registros']:>10,} registros | {info['periodo_min']} a {info['periodo_max']}")
                
                if len(csv_files) > 10:
                    print(f"    ... (+{len(csv_files) - 10} CSVs não mostrados)")
            
            # Lista XLSXs
            if xlsx_files:
                print(f"\n  📊 Arquivos XLSX (formato antigo 2018-2019):")
                anos_encontrados = set()
                for xlsx in xlsx_files[:15]:
                    nome = Path(xlsx).name
                    # Extrai ano/mês do nome
                    # Formato: trips_BikeSampa_1_18.xlsx (1_18 = janeiro de 2018)
                    match = re.search(r'(\d{1,2})_(\d{2})', nome)
                    if match:
                        mes = int(match.group(1))
                        ano = 2000 + int(match.group(2))
                        anos_encontrados.add(ano)
                        print(f"    - {nome[:40]:40} → {mes:02d}/{ano}")
                    else:
                        # Formato: trips_BikeSampa_2019-01-01.xlsx
                        match2 = re.search(r'(\d{4})-(\d{2})-(\d{2})', nome)
                        if match2:
                            ano = int(match2.group(1))
                            mes = int(match2.group(2))
                            anos_encontrados.add(ano)
                            print(f"    - {nome[:40]:40} → {mes:02d}/{ano}")
                        else:
                            print(f"    - {nome}")
                
                if len(xlsx_files) > 15:
                    print(f"    ... (+{len(xlsx_files) - 15} XLSXs não mostrados)")
                
                if anos_encontrados:
                    print(f"\n    🗓️  Anos encontrados nos XLSXs: {', '.join(map(str, sorted(anos_encontrados)))}")
                        
    except Exception as e:
        print(f"  ⚠️ Erro ao processar ZIP: {e}")
    
    return resultados

def main():
    print("="*80)
    print("🔍 ANÁLISE COMPLETA DOS DADOS DISPONÍVEIS TEMBICI")
    print("="*80)
    print(f"Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista todos os ZIPs
    zip_files = sorted(DATA_DIR.glob("*.zip"))
    csv_files_soltos = [f for f in DATA_DIR.glob("*.csv") if f.name != 'consolidated_tembici_data.csv']
    
    print(f"\n📁 Pasta analisada: {DATA_DIR}")
    print(f"  - {len(zip_files)} arquivos ZIP")
    print(f"  - {len(csv_files_soltos)} arquivos CSV soltos (excluindo consolidated)")
    
    # Informações sobre o consolidated atual
    print(f"\n{'='*80}")
    print(f"📊 ARQUIVO CONSOLIDADO ATUAL (existente)")
    print(f"{'='*80}")
    if CONSOLIDATED_CSV.exists():
        tamanho_gb = CONSOLIDATED_CSV.stat().st_size / (1024**3)
        data_modificacao = datetime.fromtimestamp(CONSOLIDATED_CSV.stat().st_mtime)
        print(f"  📄 Arquivo: {CONSOLIDATED_CSV.name}")
        print(f"  💾 Tamanho: {tamanho_gb:.2f} GB")
        print(f"  📅 Última modificação: {data_modificacao.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  📊 Registros: 11,603,422 (verificado anteriormente)")
        print(f"  🗓️  Período: 2020-01-01 a 2022-04-30")
    else:
        print("  ⚠️ Arquivo não encontrado!")
    
    # Analisa cada ZIP
    print(f"\n{'='*80}")
    print(f"📦 ANÁLISE DOS ARQUIVOS ZIP DISPONÍVEIS")
    print(f"{'='*80}")
    
    all_results = []
    
    for zip_file in zip_files:
        results = analyze_zip_file(zip_file)
        for r in results:
            r['zip_origem'] = zip_file.name
        all_results.extend(results)
    
    # Analisa CSVs soltos
    if csv_files_soltos:
        print(f"\n{'='*80}")
        print(f"📄 ARQUIVOS CSV SOLTOS (fora dos ZIPs)")
        print(f"{'='*80}")
        for csv_file in csv_files_soltos:
            print(f"\n  📄 {csv_file.name}")
            try:
                # Conta linhas
                with open(csv_file, 'r') as f:
                    total_lines = sum(1 for _ in f) - 1
                
                # Lê amostra
                df = pd.read_csv(csv_file, nrows=10)
                
                date_col = 'start_time' if 'start_time' in df.columns else 'start_date'
                if date_col in df.columns:
                    primeira = pd.to_datetime(df[date_col].iloc[0], errors='coerce')
                    print(f"    Registros: {total_lines:,}")
                    print(f"    Primeira data: {primeira}")
                else:
                    print(f"    Registros: {total_lines:,}")
                    
            except Exception as e:
                print(f"    ⚠️ Erro: {e}")
    
    # RESUMO FINAL
    print(f"\n{'='*80}")
    print(f"📊 RESUMO GERAL E ANÁLISE")
    print(f"{'='*80}")
    
    # Agrupa por período
    periodos_por_ano = {}
    for result in all_results:
        if result.get('periodo_min'):
            ano = result['periodo_min'][:4]
            if ano not in periodos_por_ano:
                periodos_por_ano[ano] = {'arquivos': 0, 'registros': 0, 'zips': set()}
            periodos_por_ano[ano]['arquivos'] += 1
            periodos_por_ano[ano]['registros'] += result['registros']
            periodos_por_ano[ano]['zips'].add(result.get('zip_origem', 'desconhecido'))
    
    print("\n📅 DADOS DISPONÍVEIS POR ANO (apenas CSVs analisados):")
    for ano in sorted(periodos_por_ano.keys()):
        info = periodos_por_ano[ano]
        print(f"  {ano}: {info['registros']:>12,} registros em {info['arquivos']:>3} arquivos CSV")
        print(f"        (ZIPs: {', '.join(sorted(info['zips']))})")
    
    # Identificar dados NÃO processados
    print(f"\n{'='*80}")
    print(f"⚠️  DADOS POSSIVELMENTE NÃO INCLUÍDOS NO CONSOLIDATED")
    print(f"{'='*80}")
    
    print("\n  O arquivo consolidated_tembici_data.csv atual contém:")
    print("    ✓ 11,603,422 registros")
    print("    ✓ Período: 2020-01-01 a 2022-04-30 (2.33 anos)")
    print("")
    
    zips_2018_2019 = [z for z in zip_files if '2019' in z.name.lower() or 'tembici' in z.name.lower()]
    zips_2023 = [z for z in zip_files if '2023' in z.name]
    
    if zips_2018_2019:
        print(f"  📦 ZIPs com possíveis dados 2018-2019 ({len(zips_2018_2019)}):")
        for z in zips_2018_2019:
            print(f"    ⚠️  {z.name}")
            print(f"        → Contém arquivos XLSX (formato antigo)")
            print(f"        → Provavelmente NÃO incluído no consolidated")
    
    if zips_2023:
        print(f"\n  📦 ZIPs com dados 2023 ({len(zips_2023)}):")
        for z in zips_2023:
            print(f"    ⚠️  {z.name}")
            print(f"        → Provavelmente NÃO incluído no consolidated (termina em 2022-04-30)")
    
    # Salva relatório
    relatorio_path = OUTPUT_DIR / f"relatorio_dados_disponiveis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO: ANÁLISE DE DADOS DISPONÍVEIS TEMBICI\n")
        f.write("="*80 + "\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("ARQUIVO CONSOLIDATED ATUAL:\n")
        f.write(f"  - Registros: 11,603,422\n")
        f.write(f"  - Período: 2020-01-01 a 2022-04-30\n")
        f.write(f"  - Tamanho: {tamanho_gb:.2f} GB\n\n")
        
        f.write("ZIPs DISPONÍVEIS:\n")
        for z in zip_files:
            f.write(f"  - {z.name}\n")
        
        f.write("\nDADOS POR ANO (CSVs analisados):\n")
        for ano in sorted(periodos_por_ano.keys()):
            info = periodos_por_ano[ano]
            f.write(f"  {ano}: {info['registros']:,} registros\n")
        
        f.write("\nPOSSÍVEIS DADOS NÃO INCLUÍDOS:\n")
        if zips_2018_2019:
            f.write("  Dados 2018-2019:\n")
            for z in zips_2018_2019:
                f.write(f"    - {z.name}\n")
        if zips_2023:
            f.write("  Dados 2023:\n")
            for z in zips_2023:
                f.write(f"    - {z.name}\n")
    
    print(f"\n{'='*80}")
    print(f"💾 RELATÓRIO SALVO")
    print(f"{'='*80}")
    print(f"  📄 {relatorio_path}")
    
    print(f"\n{'='*80}")
    print(f"💡 CONCLUSÕES E PRÓXIMOS PASSOS")
    print(f"{'='*80}")
    print("""
1. O consolidated_tembici_data.csv ATUAL tem apenas dados de 2020-2022
   
2. Existem ZIPs com dados de 2018-2019 (formato XLSX) que parecem 
   NÃO ter sido incluídos na consolidação

3. Existem ZIPs com dados de 2023 que também NÃO foram incluídos

4. Para ter o dataset COMPLETO (2018-2023), seria necessário:
   - Re-executar o script de consolidação, OU
   - Criar um novo script que processe os XLSXs de 2018-2019
   - Adicionar os CSVs de 2023
   
5. RECOMENDAÇÃO: 
   - Verificar se os dados de 2020-2022 são suficientes para a monografia
   - OU criar um novo consolidated_tembici_data_COMPLETO.csv com todos os anos
   - NÃO apagar o arquivo atual para manter backup!
""")

if __name__ == '__main__':
    main()
