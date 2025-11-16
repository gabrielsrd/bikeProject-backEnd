#!/usr/bin/env python3
"""
Tembici Data COMPLETE Consolidation Script - VERSÃO COMPLETA

Este script processa TODOS os dados disponíveis (2018-2023):
- 2018-2019: XLSXs (formato antigo)
- 2020-2022: CSVs (formato misto)
- 2022-2023: CSVs novos (formato novo)

Output: consolidated_tembici_data_COMPLETO.csv

IMPORTANTE - GEOCODIFICAÇÃO:
-----------------------------
Este script tenta adicionar coordenadas das estações usando:
1. Arquivo geojsons/estacoes.geojson (se disponível)
2. Arquivos XLSX de estações nos ZIPs extraídos

⚠️  PROBLEMA CONHECIDO: Estações antigas (2018-2019) podem não ter coordenadas
    nas fontes disponíveis, resultando em latitude/longitude NULL no CSV.

SOLUÇÃO: Após importar dados para o SQLite, execute:
    python3 scripts/fix_missing_coordinates.py

Este script de correção preenche coordenadas faltantes usando as coordenadas
médias das viagens já importadas no banco SQLite (dados reais de uso).
"""

import os
import csv
import zipfile
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import glob
from pathlib import Path
import openpyxl
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consolidacao_completa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TembiciCompleteProcessor:
    def __init__(self, data_dir, output_file):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        self.extracted_dir = self.data_dir / "extracted_COMPLETO_temp"
        self.stations_info = {}
        
        # Target CSV columns (FORMATO EXATO do consolidated_tembici_data.csv)
        self.target_columns = [
            'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
            'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
            'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
        ]
        
        # Estatísticas
        self.stats = {
            'xlsx_2018_2019': 0,
            'csv_2020': 0,
            'csv_2021': 0,
            'csv_2022_jan_apr': 0,
            'csv_2022_may_dec': 0,
            'csv_2023': 0,
            'errors': 0,
            'total': 0
        }
        
    def extract_all_zips(self):
        """Extrai TODOS os ZIPs disponíveis"""
        logger.info("="*80)
        logger.info("ETAPA 1: EXTRAINDO TODOS OS ZIPs")
        logger.info("="*80)
        
        self.extracted_dir.mkdir(exist_ok=True)
        
        zip_files = list(self.data_dir.glob("*.zip"))
        logger.info(f"Encontrados {len(zip_files)} arquivos ZIP")
        
        for zip_file in zip_files:
            try:
                logger.info(f"\n📦 Extraindo: {zip_file.name} ({zip_file.stat().st_size / 1024 / 1024:.1f} MB)")
                
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    extract_subdir = self.extracted_dir / zip_file.stem
                    extract_subdir.mkdir(exist_ok=True)
                    zip_ref.extractall(extract_subdir)
                    
                    # Listar alguns arquivos extraídos
                    members = zip_ref.namelist()
                    logger.info(f"   ✓ Extraídos {len(members)} arquivos")
                    if members:
                        logger.info(f"   Primeiros: {members[:3]}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao extrair {zip_file}: {e}")
                
        logger.info(f"\n✓ Extração completa!")
                
    def load_station_coordinates(self):
        """Carrega coordenadas das estações de múltiplas fontes"""
        logger.info("\n" + "="*80)
        logger.info("ETAPA 2: CARREGANDO COORDENADAS DAS ESTAÇÕES")
        logger.info("="*80)
        
        # 1. Tentar GeoJSON principal (estacoes.geojson)
        stations_geojson = self.data_dir.parent.parent / "geojsons" / "estacoes.geojson"
        if stations_geojson.exists():
            try:
                logger.info(f"📍 Carregando: {stations_geojson}")
                with open(stations_geojson, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for feature in data.get('features', []):
                        props = feature.get('properties', {})
                        coords = feature.get('geometry', {}).get('coordinates', [])
                        if len(coords) >= 2:
                            station_name = props.get('nome') or props.get('name') or props.get('station_name')
                            if station_name:
                                self.stations_info[station_name] = {
                                    'latitude': coords[1],
                                    'longitude': coords[0]
                                }
                logger.info(f"   ✓ Carregadas {len(self.stations_info)} estações de estacoes.geojson")
            except Exception as e:
                logger.warning(f"   ⚠ Erro ao carregar estacoes.geojson: {e}")
        else:
            logger.info(f"   ℹ️  estacoes.geojson não encontrado (normal para dados antigos)")
        
        # 2. Procurar arquivos XLSX de estações nos ZIPs extraídos
        xlsx_stations = list(self.extracted_dir.glob("**/Estações*.xlsx"))
        for xlsx_file in xlsx_stations:
            try:
                logger.info(f"📊 Processando estações XLSX: {xlsx_file.name}")
                df = pd.read_excel(xlsx_file)
                
                # Tentar diferentes variações de nomes de colunas
                name_col = None
                lat_col = None
                lon_col = None
                
                for col in df.columns:
                    col_lower = str(col).lower()
                    if any(x in col_lower for x in ['nome', 'name', 'estação', 'estacao', 'station']):
                        name_col = col
                    if any(x in col_lower for x in ['lat']):
                        lat_col = col
                    if any(x in col_lower for x in ['lon', 'lng']):
                        lon_col = col
                
                if name_col and lat_col and lon_col:
                    count_before = len(self.stations_info)
                    for _, row in df.iterrows():
                        station_name = str(row[name_col]).strip()
                        if station_name and station_name != 'nan':
                            try:
                                self.stations_info[station_name] = {
                                    'latitude': float(row[lat_col]),
                                    'longitude': float(row[lon_col])
                                }
                            except:
                                pass
                    logger.info(f"   ✓ +{len(self.stations_info) - count_before} novas estações")
                    
            except Exception as e:
                logger.warning(f"   ⚠ Erro ao processar {xlsx_file.name}: {e}")
        
        logger.info(f"\n✓ Total de estações com coordenadas: {len(self.stations_info)}")
    
    def get_station_coordinates(self, station_name):
        """Obtém coordenadas de uma estação"""
        if not station_name or pd.isna(station_name):
            return None, None
            
        station_name = str(station_name).strip()
        
        # Match direto
        if station_name in self.stations_info:
            info = self.stations_info[station_name]
            return info['latitude'], info['longitude']
        
        # Match parcial
        for stored_name, info in self.stations_info.items():
            if station_name.lower() in stored_name.lower() or stored_name.lower() in station_name.lower():
                return info['latitude'], info['longitude']
        
        return None, None
    
    def process_xlsx_old_format(self, file_path):
        """
        Processa XLSX 2018-2019 (formato mais antigo)
        Colunas esperadas: start_date, end_date, start_station_name, end_station_name, 
                          duration_seconds, ano_nasc, etc
        """
        try:
            logger.info(f"   📄 XLSX antigo: {file_path.name}")
            
            # Ler XLSX
            df = pd.read_excel(file_path)
            
            if df.empty:
                logger.warning(f"      ⚠ Arquivo vazio")
                return None
            
            logger.info(f"      Linhas: {len(df)}")
            logger.info(f"      Colunas: {list(df.columns)[:5]}...")
            
            normalized_data = []
            
            for idx, row in df.iterrows():
                try:
                    # trip_id (gerar - formato antigo não tem)
                    year_month = file_path.stem.split('_')[-1]  # Ex: 2019-01-01
                    trip_id = f"{year_month}_{idx}_BikeSampa"
                    
                    # duration_seconds
                    duration = row.get('duration_seconds', 0)
                    try:
                        duration = int(float(duration)) if duration else 0
                    except:
                        duration = 0
                    
                    # Station names
                    initial_station = str(row.get('start_station_name', '')).strip()
                    final_station = str(row.get('end_station_name', '')).strip()
                    
                    # Timestamps
                    start_time = row.get('start_date', '')
                    end_time = row.get('end_date', '')
                    
                    # Converter para ISO format se necessário
                    if start_time and not isinstance(start_time, str):
                        try:
                            start_time = pd.to_datetime(start_time).strftime('%Y-%m-%dT%H:%M:%SZ')
                        except:
                            start_time = str(start_time)
                    elif start_time and isinstance(start_time, str) and not start_time.endswith('Z'):
                        try:
                            dt = pd.to_datetime(start_time, errors='coerce')
                            if pd.notna(dt):
                                start_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        except:
                            pass
                    
                    if end_time and not isinstance(end_time, str):
                        try:
                            end_time = pd.to_datetime(end_time).strftime('%Y-%m-%dT%H:%M:%SZ')
                        except:
                            end_time = str(end_time)
                    elif end_time and isinstance(end_time, str) and not end_time.endswith('Z'):
                        try:
                            dt = pd.to_datetime(end_time, errors='coerce')
                            if pd.notna(dt):
                                end_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        except:
                            pass
                    
                    # Birth year
                    birth_year = row.get('ano_nasc', '')
                    if birth_year and str(birth_year) != 'nan':
                        try:
                            year_int = int(float(str(birth_year)))
                            if 1900 <= year_int <= 2010:
                                birth_year = f"{year_int}-01-01"
                            else:
                                birth_year = ""
                        except:
                            birth_year = ""
                    else:
                        birth_year = ""
                    
                    # Coordenadas
                    init_lat, init_lon = self.get_station_coordinates(initial_station)
                    final_lat, final_lon = self.get_station_coordinates(final_station)
                    
                    normalized_row = {
                        'trip_id': trip_id,
                        'duration_seconds': duration,
                        'initial_station_name': initial_station,
                        'start_time': start_time,
                        'final_station_name': final_station,
                        'end_time': end_time,
                        'birth_year': birth_year,
                        'initial_station_latitude': init_lat if init_lat is not None else '',
                        'initial_station_longitude': init_lon if init_lon is not None else '',
                        'final_station_latitude': final_lat if final_lat is not None else '',
                        'final_station_longitude': final_lon if final_lon is not None else ''
                    }
                    
                    normalized_data.append(normalized_row)
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    if idx < 5:  # Log apenas primeiros erros
                        logger.warning(f"      ⚠ Erro linha {idx}: {e}")
                    continue
            
            result_df = pd.DataFrame(normalized_data)
            logger.info(f"      ✓ Processadas {len(result_df)} linhas")
            return result_df
            
        except Exception as e:
            logger.error(f"      ❌ Erro ao processar {file_path}: {e}")
            return None
    
    def process_csv_new_format(self, file_path):
        """
        Processa CSV 2020-2023 (formato novo)
        Colunas: trip_id, duration_seconds, initial_station_name, start_time, etc
        """
        try:
            logger.info(f"   📄 CSV novo: {file_path.name}")
            
            # Tentar diferentes encodings
            df = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None or df.empty:
                logger.warning(f"      ⚠ Não foi possível ler ou arquivo vazio")
                return None
            
            logger.info(f"      Linhas: {len(df)}")
            logger.info(f"      Colunas: {list(df.columns)[:5]}...")
            
            # Verificar se já está no formato correto
            if all(col in df.columns for col in self.target_columns):
                logger.info(f"      ✓ Já no formato correto!")
                return df[self.target_columns]
            
            # Se não, tentar normalizar
            normalized_data = []
            
            for idx, row in df.iterrows():
                try:
                    normalized_row = {
                        'trip_id': row.get('trip_id', f"{file_path.stem}_{idx}_BikeSampa"),
                        'duration_seconds': row.get('duration_seconds', ''),
                        'initial_station_name': row.get('initial_station_name', ''),
                        'start_time': row.get('start_time', ''),
                        'final_station_name': row.get('final_station_name', ''),
                        'end_time': row.get('end_time', ''),
                        'birth_year': row.get('birth_year', ''),
                        'initial_station_latitude': row.get('initial_station_latitude', ''),
                        'initial_station_longitude': row.get('initial_station_longitude', ''),
                        'final_station_latitude': row.get('final_station_latitude', ''),
                        'final_station_longitude': row.get('final_station_longitude', '')
                    }
                    
                    normalized_data.append(normalized_row)
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    if idx < 5:
                        logger.warning(f"      ⚠ Erro linha {idx}: {e}")
                    continue
            
            result_df = pd.DataFrame(normalized_data)
            logger.info(f"      ✓ Processadas {len(result_df)} linhas")
            return result_df
            
        except Exception as e:
            logger.error(f"      ❌ Erro ao processar {file_path}: {e}")
            return None
    
    def find_and_process_all_files(self):
        """Encontra e processa TODOS os arquivos"""
        logger.info("\n" + "="*80)
        logger.info("ETAPA 3: PROCESSANDO TODOS OS ARQUIVOS")
        logger.info("="*80)
        
        all_dataframes = []
        
        # 1. XLSX 2018-2019
        logger.info("\n📊 1. Processando XLSXs 2018-2019...")
        xlsx_files = list(self.extracted_dir.glob("**/*.xlsx"))
        xlsx_files = [f for f in xlsx_files if 'trips_BikeSampa' in f.name or 'viagens' in f.name.lower()]
        logger.info(f"   Encontrados {len(xlsx_files)} arquivos XLSX de viagens")
        
        for xlsx_file in xlsx_files:
            df = self.process_xlsx_old_format(xlsx_file)
            if df is not None and not df.empty:
                all_dataframes.append(df)
                self.stats['xlsx_2018_2019'] += len(df)
        
        # 2. CSVs extraídos dos ZIPs
        logger.info("\n📄 2. Processando CSVs extraídos dos ZIPs...")
        csv_files = list(self.extracted_dir.glob("**/*.csv"))
        csv_files = [f for f in csv_files if 'trips_BikeSampa' in f.name or 'viagens' in f.name.lower()]
        csv_files = [f for f in csv_files if not any(x in f.name for x in ['Bogota', 'Zone.Identifier'])]
        logger.info(f"   Encontrados {len(csv_files)} arquivos CSV")
        
        for csv_file in csv_files:
            df = self.process_csv_new_format(csv_file)
            if df is not None and not df.empty:
                all_dataframes.append(df)
                
                # Classificar por período
                filename = csv_file.name
                if '2020' in filename:
                    self.stats['csv_2020'] += len(df)
                elif '2021' in filename:
                    self.stats['csv_2021'] += len(df)
                elif '2022' in filename:
                    # Verificar se é Jan-Apr ou Mai-Dez
                    month_match = filename.split('2022-')[1][:2] if '2022-' in filename else '00'
                    if month_match in ['01', '02', '03', '04']:
                        self.stats['csv_2022_jan_apr'] += len(df)
                    else:
                        self.stats['csv_2022_may_dec'] += len(df)
                elif '2023' in filename:
                    self.stats['csv_2023'] += len(df)
        
        # 3. CSV solto na pasta principal (2022-07)
        logger.info("\n📄 3. Processando CSVs soltos na pasta principal...")
        loose_csvs = list(self.data_dir.glob("*.csv"))
        loose_csvs = [f for f in loose_csvs if 'trips_BikeSampa' in f.name]
        logger.info(f"   Encontrados {len(loose_csvs)} arquivos CSV soltos")
        
        for csv_file in loose_csvs:
            df = self.process_csv_new_format(csv_file)
            if df is not None and not df.empty:
                all_dataframes.append(df)
                if '2022' in csv_file.name:
                    self.stats['csv_2022_may_dec'] += len(df)
        
        logger.info(f"\n✓ Total de DataFrames coletados: {len(all_dataframes)}")
        
        return all_dataframes
    
    def consolidate(self):
        """Método principal"""
        logger.info("\n" + "="*80)
        logger.info("🚀 INICIANDO CONSOLIDAÇÃO COMPLETA DOS DADOS TEMBICI")
        logger.info("="*80)
        logger.info(f"Diretório de entrada: {self.data_dir}")
        logger.info(f"Arquivo de saída: {self.output_file}")
        
        # ETAPA 1: Extrair ZIPs
        self.extract_all_zips()
        
        # ETAPA 2: Carregar coordenadas
        self.load_station_coordinates()
        
        # ETAPA 3: Processar todos os arquivos
        all_dataframes = self.find_and_process_all_files()
        
        if not all_dataframes:
            logger.error("❌ Nenhum dado válido encontrado!")
            return False
        
        # ETAPA 4: Combinar tudo
        logger.info("\n" + "="*80)
        logger.info("ETAPA 4: COMBINANDO TODOS OS DADOS")
        logger.info("="*80)
        
        logger.info("Concatenando DataFrames...")
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Garantir todas as colunas
        for col in self.target_columns:
            if col not in final_df.columns:
                final_df[col] = ''
        
        # Reordenar colunas
        final_df = final_df[self.target_columns]
        
        # Calcular total
        self.stats['total'] = len(final_df)
        
        # ETAPA 5: Salvar
        logger.info("\n" + "="*80)
        logger.info("ETAPA 5: SALVANDO ARQUIVO FINAL")
        logger.info("="*80)
        
        logger.info(f"Salvando {len(final_df)} registros...")
        self.output_file.parent.mkdir(exist_ok=True, parents=True)
        final_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        file_size_mb = self.output_file.stat().st_size / 1024 / 1024
        logger.info(f"✓ Arquivo salvo: {file_size_mb:.2f} MB")
        
        # ETAPA 6: Estatísticas finais
        self.print_final_stats()
        
        # Cleanup
        logger.info("\n🧹 Limpando arquivos temporários...")
        if self.extracted_dir.exists():
            import shutil
            shutil.rmtree(self.extracted_dir)
            logger.info("✓ Arquivos temporários removidos")
        
        return True
    
    def print_final_stats(self):
        """Imprime estatísticas finais"""
        logger.info("\n" + "="*80)
        logger.info("📊 ESTATÍSTICAS FINAIS")
        logger.info("="*80)
        logger.info(f"""
2018-2019 (XLSX):           {self.stats['xlsx_2018_2019']:>12,} registros
2020 (CSV):                 {self.stats['csv_2020']:>12,} registros
2021 (CSV):                 {self.stats['csv_2021']:>12,} registros
2022 Jan-Abr (CSV):         {self.stats['csv_2022_jan_apr']:>12,} registros
2022 Mai-Dez (CSV):         {self.stats['csv_2022_may_dec']:>12,} registros
2023 (CSV):                 {self.stats['csv_2023']:>12,} registros
─────────────────────────────────────────────
TOTAL:                      {self.stats['total']:>12,} registros
Erros encontrados:          {self.stats['errors']:>12,} linhas

Arquivo de saída: {self.output_file}
Tamanho: {self.output_file.stat().st_size / 1024 / 1024:.2f} MB
""")
        logger.info("="*80)

def main():
    """Função principal"""
    # Configuração
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "dataRaw" / "Tembici-SaoPaulo"
    output_file = script_dir / "dataRaw" / "consolidated_tembici_data_COMPLETO.csv"
    
    # Banner
    print("\n" + "="*80)
    print("🚴 CONSOLIDADOR COMPLETO DE DADOS TEMBICI")
    print("="*80)
    print(f"Versão: 2.0 - DATASET COMPLETO (2018-2023)")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Verificar se diretório existe
    if not data_dir.exists():
        print(f"❌ ERRO: Diretório não encontrado: {data_dir}")
        return
    
    # Criar processador
    processor = TembiciCompleteProcessor(data_dir, output_file)
    
    # Executar consolidação
    success = processor.consolidate()
    
    # Resultado final
    if success:
        print("\n" + "="*80)
        print("✅ SUCESSO! CONSOLIDAÇÃO COMPLETA!")
        print("="*80)
        print(f"Arquivo gerado: {output_file}")
        print(f"Total de registros: {processor.stats['total']:,}")
        print("\nPróximo passo: Importar para SQLite usando import_to_sqlite_COMPLETO.py")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("❌ FALHA NA CONSOLIDAÇÃO")
        print("="*80)
        print("Verifique os logs em: consolidacao_completa.log")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
