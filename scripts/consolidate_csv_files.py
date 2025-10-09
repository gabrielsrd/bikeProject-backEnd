#!/usr/bin/env python3
"""
Tembici Data Consolidator

This script reads extracted CSV files and appends them to a single consolidated CSV file.
Processes files incrementally to avoid memory issues.
"""

import os
import csv
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TembiciConsolidator:
    def __init__(self, data_dir, output_file):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        
        # Target CSV columns (same as userTrips.csv)
        self.target_columns = [
            'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
            'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
            'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
        ]
        
    def identify_csv_format(self, csv_file):
        """Identify the format of a CSV file by examining its headers"""
        try:
            # Read just the header
            df_sample = pd.read_csv(csv_file, nrows=0, encoding='utf-8')
            columns = set(df_sample.columns)
            
            # Format #1: Already matches target (47 files)
            if 'trip_id' in columns and 'initial_station_name' in columns:
                return 'format_1'
            
            # Format #2: Spanish format with id_recorrido (36 files)
            elif 'id_recorrido' in columns and 'nombre_estacion_origen' in columns:
                return 'format_2'
            
            # Format #3: Spanish format with id_usuario (7 files)  
            elif 'id_usuario' in columns and 'nombre_estacion_origen' in columns:
                return 'format_3'
            
            else:
                logger.warning(f"Unknown format in {csv_file}: {list(columns)}")
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Error reading {csv_file}: {e}")
            return None
    
    def convert_row_to_target_format(self, row, csv_format, file_name, row_idx):
        """Convert a row from any format to target format"""
        result = {}
        
        if csv_format == 'format_1':
            # Format #1: Already matches target format perfectly (47 files)
            result = {
                'trip_id': row.get('trip_id', f"{file_name}_{row_idx}_BikeSampa"),
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
            
        elif csv_format == 'format_2':
            # Format #2: Spanish format with id_recorrido (36 files)
            result = {
                'trip_id': row.get('id_recorrido', f"{file_name}_{row_idx}_BikeSampa"),
                'duration_seconds': row.get('duracion_recorrido', ''),
                'initial_station_name': row.get('nombre_estacion_origen', ''),
                'start_time': self.convert_datetime(row.get('fecha_origen_recorrido', '')),
                'final_station_name': row.get('nombre_estacion_destino', ''),
                'end_time': self.convert_datetime(row.get('fecha_destino_recorrido', '')),
                'birth_year': '',  # Missing in this format
                'initial_station_latitude': row.get('lat_estacion_origen', ''),
                'initial_station_longitude': row.get('long_estacion_origen', ''),
                'final_station_latitude': row.get('lat_estacion_destino', ''),
                'final_station_longitude': row.get('long_estacion_destino', '')
            }
            
        elif csv_format == 'format_3':
            # Format #3: Spanish format with id_usuario (7 files)
            result = {
                'trip_id': row.get('id_usuario', f"{file_name}_{row_idx}_BikeSampa"),
                'duration_seconds': row.get('duracion_recorrido', ''),
                'initial_station_name': row.get('nombre_estacion_origen', ''),
                'start_time': self.convert_datetime(row.get('fecha_origen_recorrido', '')),
                'final_station_name': row.get('nombre_estacion_destino', ''),
                'end_time': self.convert_datetime(row.get('fecha_destino_recorrido', '')),
                'birth_year': '',  # Missing in this format
                'initial_station_latitude': row.get('lat_estacion_origen', ''),
                'initial_station_longitude': row.get('long_estacion_origen', ''),
                'final_station_latitude': row.get('lat_estacion_destino', ''),
                'final_station_longitude': row.get('long_estacion_destino', '')
            }
        
        # Clean up any NaN values
        for key, value in result.items():
            if pd.isna(value):
                result[key] = ''
            else:
                result[key] = str(value)
        
        return result
    
    def convert_datetime(self, dt_str):
        """Convert datetime string to ISO format"""
        if not dt_str or pd.isna(dt_str):
            return ''
        
        try:
            dt_str = str(dt_str)
            if dt_str.endswith('Z'):
                return dt_str
            
            # Try to parse and convert to ISO format
            dt = pd.to_datetime(dt_str)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            return dt_str  # Return original if conversion fails
    
    def process_csv_file(self, csv_file, writer, chunk_size=5000):
        """Process a single CSV file and append to output"""
        csv_format = self.identify_csv_format(csv_file)
        if not csv_format or csv_format == 'unknown':
            logger.warning(f"Skipping {csv_file.name} - unknown format")
            return 0
        
        # Show format mapping
        format_names = {
            'format_1': 'Target Format (trip_id + coordinates)',
            'format_2': 'Spanish Format (id_recorrido)',
            'format_3': 'Spanish Format (id_usuario)'
        }
        
        logger.info(f"Processing {csv_file.name} as {format_names.get(csv_format, csv_format)}")
        
        total_rows = 0
        
        try:
            # Process in chunks
            for chunk_num, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size, encoding='utf-8')):
                logger.info(f"  Processing chunk {chunk_num + 1} ({len(chunk)} rows)")
                
                for idx, row in chunk.iterrows():
                    try:
                        formatted_row = self.convert_row_to_target_format(
                            row, csv_format, csv_file.stem, total_rows + idx
                        )
                        writer.writerow(formatted_row)
                        total_rows += 1
                        
                        if total_rows % 10000 == 0:
                            logger.info(f"    Written {total_rows:,} rows")
                            
                    except Exception as e:
                        logger.warning(f"Error processing row {idx}: {e}")
                        continue
            
            logger.info(f"✓ Completed {csv_file.name}: {total_rows:,} rows")
            return total_rows
            
        except Exception as e:
            logger.error(f"✗ Error processing {csv_file.name}: {e}")
            return 0
    
    def find_csv_files(self):
        """Find all CSV files in the data directory"""
        csv_files = []
        
        # Look in main directory
        main_csvs = [f for f in self.data_dir.glob("*.csv") if not f.name.endswith(':Zone.Identifier')]
        csv_files.extend(main_csvs)
        
        # Look in extracted directory
        extracted_dir = self.data_dir / "extracted"
        if extracted_dir.exists():
            extracted_csvs = [f for f in extracted_dir.glob("**/*.csv") if not f.name.endswith(':Zone.Identifier')]
            csv_files.extend(extracted_csvs)
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        return csv_files
    
    def consolidate(self):
        """Main consolidation method"""
        logger.info("Starting Tembici data consolidation...")
        
        # Find all CSV files
        csv_files = self.find_csv_files()
        
        if not csv_files:
            logger.error("No CSV files found!")
            return False
        
        # Create output directory
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Process files and write to output
        total_rows = 0
        processed_files = 0
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=self.target_columns)
            writer.writeheader()
            
            for csv_file in csv_files:
                try:
                    rows_written = self.process_csv_file(csv_file, writer)
                    total_rows += rows_written
                    processed_files += 1
                    
                    logger.info(f"Progress: {processed_files}/{len(csv_files)} files, {total_rows:,} total rows")
                    
                except Exception as e:
                    logger.error(f"Failed to process {csv_file}: {e}")
                    continue
        
        logger.info(f"\n✅ Consolidation complete!")
        logger.info(f"Processed: {processed_files}/{len(csv_files)} files")
        logger.info(f"Total rows: {total_rows:,}")
        logger.info(f"Output file: {self.output_file}")
        
        return True

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "dataRaw" / "Tembici-SaoPaulo"
    output_file = script_dir / ".." / "dataClean" / "consolidated_tembici_trips.csv"
    
    consolidator = TembiciConsolidator(data_dir, output_file)
    success = consolidator.consolidate()
    
    if success:
        print(f"\n✅ SUCCESS: Consolidated CSV created at {output_file}")
        print(f"The file follows the same format as userTrips.csv")
    else:
        print(f"\n❌ FAILED: Could not consolidate the data")

if __name__ == "__main__":
    main()