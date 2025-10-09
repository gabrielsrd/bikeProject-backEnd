#!/usr/bin/env python3
"""
Efficient Tembici Data Consolidation Script

This script processes Tembici-SaoPaulo data efficiently by:
1. First extracting and examining all files to understand formats
2. Processing files one by one and appending directly to output CSV
3. Using minimal memory footprint

Target format (userTrips.csv):
trip_id,duration_seconds,initial_station_name,start_time,final_station_name,end_time,birth_year,initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
"""

import os
import csv
import zipfile
import pandas as pd
from datetime import datetime
import logging
import glob
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EfficientTembiciProcessor:
    def __init__(self, data_dir, output_file):
        self.data_dir = Path(data_dir)
        self.output_file = output_file
        self.extracted_dir = self.data_dir / "extracted_temp"
        
        # Target CSV columns
        self.target_columns = [
            'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
            'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
            'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
        ]
        
        # Format mappings for different CSV types
        self.format_mappings = {
            # New format (2022+) - already matches target
            'new_format': {
                'trip_id': 'trip_id',
                'duration_seconds': 'duration_seconds',
                'initial_station_name': 'initial_station_name',
                'start_time': 'start_time',
                'final_station_name': 'final_station_name',
                'end_time': 'end_time',
                'birth_year': 'birth_year',
                'initial_station_latitude': 'initial_station_latitude',
                'initial_station_longitude': 'initial_station_longitude',
                'final_station_latitude': 'final_station_latitude',
                'final_station_longitude': 'final_station_longitude'
            },
            # Old format (2018-2019)
            'old_format': {
                'duration_seconds': 'duration_seconds',
                'initial_station_name': 'start_station_name',
                'start_time': 'start_date',
                'final_station_name': 'end_station_name',
                'end_time': 'end_date',
                'birth_year': 'ano_nasc'
            },
            # Spanish format
            'spanish_format': {
                'trip_id': 'id_recorrido',
                'duration_seconds': 'duracion_recorrido',
                'initial_station_name': 'nombre_estacion_origen',
                'start_time': 'fecha_origen_recorrido',
                'final_station_name': 'nombre_estacion_destino',
                'end_time': 'fecha_destino_recorrido',
                'initial_station_latitude': 'lat_estacion_origen',
                'initial_station_longitude': 'long_estacion_origen',
                'final_station_latitude': 'lat_estacion_destino',
                'final_station_longitude': 'long_estacion_destino'
            }
        }

    def extract_zip_files(self):
        """Extract all ZIP files in the data directory"""
        logger.info("Extracting ZIP files...")
        
        # Create extraction directory
        self.extracted_dir.mkdir(exist_ok=True)
        
        zip_files = list(self.data_dir.glob("*.zip"))
        logger.info(f"Found {len(zip_files)} ZIP files to extract")
        
        for zip_file in zip_files:
            try:
                logger.info(f"Extracting {zip_file.name}")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Create subdirectory for this zip
                    extract_subdir = self.extracted_dir / zip_file.stem
                    extract_subdir.mkdir(exist_ok=True)
                    zip_ref.extractall(extract_subdir)
                    
            except Exception as e:
                logger.error(f"Error extracting {zip_file}: {e}")

    def identify_csv_format(self, csv_file):
        """Identify the format of a CSV file by examining its headers"""
        try:
            # Read just the header
            df_sample = pd.read_csv(csv_file, nrows=0, encoding='utf-8')
            columns = set(df_sample.columns)
            
            # Check for new format (has trip_id and initial_station_name)
            if 'trip_id' in columns and 'initial_station_name' in columns:
                return 'new_format'
            
            # Check for old format (has start_station_name and duration_seconds)
            elif 'start_station_name' in columns and 'duration_seconds' in columns:
                return 'old_format'
            
            # Check for Spanish format (has id_recorrido)
            elif 'id_recorrido' in columns:
                return 'spanish_format'
            
            else:
                logger.warning(f"Unknown format in {csv_file}: {list(columns)}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading {csv_file}: {e}")
            return None

    def process_csv_chunk(self, csv_file, chunk_size=10000):
        """Process a CSV file in chunks and yield formatted rows"""
        csv_format = self.identify_csv_format(csv_file)
        if not csv_format:
            return
            
        logger.info(f"Processing {csv_file.name} as {csv_format}")
        
        try:
            # Process in chunks to avoid memory issues
            chunk_iter = pd.read_csv(csv_file, chunksize=chunk_size, encoding='utf-8')
            
            for chunk_num, chunk in enumerate(chunk_iter):
                logger.info(f"  Processing chunk {chunk_num + 1} ({len(chunk)} rows)")
                
                for idx, row in chunk.iterrows():
                    try:
                        # Create formatted row based on format
                        formatted_row = self.format_row(row, csv_format, csv_file, idx)
                        if formatted_row:
                            yield formatted_row
                    except Exception as e:
                        logger.warning(f"Error processing row {idx}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing {csv_file}: {e}")

    def format_row(self, row, csv_format, file_path, row_idx):
        """Format a single row according to target format"""
        formatted = {}
        mapping = self.format_mappings[csv_format]
        
        # Handle each target column
        for target_col in self.target_columns:
            if target_col in mapping:
                source_col = mapping[target_col]
                value = row.get(source_col, '')
                
                # Special handling for different fields
                if target_col == 'trip_id' and (not value or pd.isna(value)):
                    value = f"{file_path.stem}_{row_idx}_BikeSampa"
                elif target_col == 'birth_year' and value and not pd.isna(value):
                    # Convert birth year to YYYY-01-01 format
                    try:
                        if str(value).isdigit():
                            value = f"{int(value)}-01-01"
                        elif '-01-01' not in str(value):
                            year = str(value)[:4]
                            if year.isdigit():
                                value = f"{year}-01-01"
                    except:
                        value = ''
                elif target_col in ['start_time', 'end_time'] and value and not pd.isna(value):
                    # Ensure datetime is in ISO format
                    try:
                        if not str(value).endswith('Z'):
                            dt = pd.to_datetime(value)
                            value = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                    except:
                        pass  # Keep original value if conversion fails
                        
                formatted[target_col] = value if not pd.isna(value) else ''
            else:
                formatted[target_col] = ''
        
        return formatted

    def find_all_csv_files(self):
        """Find all CSV files excluding cleaned folder"""
        csv_files = []
        
        # CSV files in main directory
        main_csvs = list(self.data_dir.glob("*.csv"))
        csv_files.extend([f for f in main_csvs if not f.name.endswith(':Zone.Identifier')])
        
        # CSV files in extracted directories
        if self.extracted_dir.exists():
            extracted_csvs = list(self.extracted_dir.glob("**/*.csv"))
            csv_files.extend([f for f in extracted_csvs if not f.name.endswith(':Zone.Identifier')])
        
        logger.info(f"Found {len(csv_files)} CSV files to process (excluding cleaned folder)")
        return csv_files

    def consolidate_data(self):
        """Main method to consolidate all data efficiently"""
        logger.info("Starting efficient Tembici data consolidation...")
        
        # Step 1: Extract ZIP files
        self.extract_zip_files()
        
        # Step 2: Find all CSV files
        csv_files = self.find_all_csv_files()
        
        # Step 3: Create output file and write header
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_rows = 0
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=self.target_columns)
            writer.writeheader()
            
            # Step 4: Process each CSV file and append to output
            for csv_file in csv_files:
                file_rows = 0
                try:
                    for formatted_row in self.process_csv_chunk(csv_file):
                        writer.writerow(formatted_row)
                        file_rows += 1
                        total_rows += 1
                        
                        # Log progress every 10000 rows
                        if total_rows % 10000 == 0:
                            logger.info(f"  Total rows written: {total_rows:,}")
                    
                    logger.info(f"✓ Completed {csv_file.name}: {file_rows:,} rows")
                    
                except Exception as e:
                    logger.error(f"✗ Failed to process {csv_file.name}: {e}")
                    continue
        
        logger.info(f"✅ Consolidation complete! Total rows: {total_rows:,}")
        logger.info(f"Output saved to: {output_path}")
        
        # Cleanup
        if self.extracted_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.extracted_dir)
                logger.info("Cleaned up temporary extraction directory")
            except Exception as e:
                logger.warning(f"Could not clean up temp directory: {e}")
        
        return True

def main():
    """Main function"""
    # Configuration
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "dataRaw" / "Tembici-SaoPaulo"
    output_file = script_dir / ".." / "dataClean" / "consolidated_tembici_trips.csv"
    
    # Create processor and run
    processor = EfficientTembiciProcessor(data_dir, output_file)
    success = processor.consolidate_data()
    
    if success:
        print(f"\n✅ SUCCESS: Consolidated Tembici data saved to {output_file}")
        print(f"The file is now in the same format as userTrips.csv")
    else:
        print("\n❌ FAILED: Could not consolidate the data")

if __name__ == "__main__":
    main()