#!/usr/bin/env python3
"""
Simple Tembici Data Consolidation Script

This script processes Tembici-SaoPaulo data and consolidates them into a single CSV file
following the userTrips.csv format. It ignores the cleaned folder and focuses on 
processing ZIP files and direct CSV files.
"""

import os
import csv
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_zip_files(data_dir):
    """Extract all ZIP files in the data directory"""
    logger.info("Extracting ZIP files...")
    
    extracted_dir = data_dir / "extracted_temp"
    extracted_dir.mkdir(exist_ok=True)
    
    zip_files = [f for f in data_dir.glob("*.zip") if not f.name.endswith(':Zone.Identifier')]
    logger.info(f"Found {len(zip_files)} ZIP files to extract")
    
    for zip_file in zip_files:
        try:
            logger.info(f"Extracting {zip_file.name}")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                extract_subdir = extracted_dir / zip_file.stem
                extract_subdir.mkdir(exist_ok=True)
                zip_ref.extractall(extract_subdir)
        except Exception as e:
            logger.error(f"Error extracting {zip_file}: {e}")
    
    return extracted_dir

def process_csv_file(file_path):
    """Process a single CSV file and return normalized data"""
    try:
        logger.info(f"Processing {file_path}")
        
        # Try different encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            logger.error(f"Could not read {file_path} with any encoding")
            return []
        
        if df.empty:
            logger.warning(f"Empty file: {file_path}")
            return []
        
        logger.info(f"File has {len(df)} rows and columns: {list(df.columns)}")
        
        normalized_data = []
        columns = df.columns.tolist()
        
        for idx, row in df.iterrows():
            try:
                # Generate a simple trip_id if not present
                trip_id = row.get('trip_id', f"{Path(file_path).stem}_{idx}_BikeSampa")
                
                # Handle duration
                duration = row.get('duration_seconds', 0)
                try:
                    duration = int(float(duration)) if duration and str(duration) != 'nan' else 0
                except:
                    duration = 0
                
                # Handle station names
                if 'initial_station_name' in columns:
                    # New format
                    initial_station = str(row.get('initial_station_name', '')).strip()
                    final_station = str(row.get('final_station_name', '')).strip()
                    start_time = str(row.get('start_time', '')).strip()
                    end_time = str(row.get('end_time', '')).strip()
                    birth_year = str(row.get('birth_year', '')).strip()
                    init_lat = row.get('initial_station_latitude', '')
                    init_lon = row.get('initial_station_longitude', '')
                    final_lat = row.get('final_station_latitude', '')
                    final_lon = row.get('final_station_longitude', '')
                else:
                    # Old format
                    initial_station = str(row.get('start_station_name', '')).strip()
                    final_station = str(row.get('end_station_name', '')).strip()
                    start_time = str(row.get('start_date', '')).strip()
                    end_time = str(row.get('end_date', '')).strip()
                    
                    # Convert birth year from ano_nasc
                    ano_nasc = row.get('ano_nasc', '')
                    birth_year = ''
                    if ano_nasc and str(ano_nasc) != 'nan':
                        try:
                            year = int(float(ano_nasc))
                            if 1900 <= year <= 2010:
                                birth_year = f"{year}-01-01"
                        except:
                            pass
                    
                    # No coordinates in old format
                    init_lat = init_lon = final_lat = final_lon = ''
                
                # Clean up the values
                if start_time == 'nan': start_time = ''
                if end_time == 'nan': end_time = ''
                if birth_year == 'nan': birth_year = ''
                if str(init_lat) == 'nan': init_lat = ''
                if str(init_lon) == 'nan': init_lon = ''
                if str(final_lat) == 'nan': final_lat = ''
                if str(final_lon) == 'nan': final_lon = ''
                
                normalized_row = {
                    'trip_id': trip_id,
                    'duration_seconds': duration,
                    'initial_station_name': initial_station,
                    'start_time': start_time,
                    'final_station_name': final_station,
                    'end_time': end_time,
                    'birth_year': birth_year,
                    'initial_station_latitude': init_lat,
                    'initial_station_longitude': init_lon,
                    'final_station_latitude': final_lat,
                    'final_station_longitude': final_lon
                }
                
                normalized_data.append(normalized_row)
                
            except Exception as e:
                logger.warning(f"Error processing row {idx} in {file_path}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(normalized_data)} rows from {file_path}")
        return normalized_data
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []

def find_csv_files(data_dir, extracted_dir):
    """Find all CSV files, excluding the cleaned folder"""
    csv_files = []
    
    # CSV files directly in data directory (excluding cleaned folder)
    for csv_file in data_dir.glob("*.csv"):
        if not csv_file.name.endswith(':Zone.Identifier'):
            csv_files.append(csv_file)
    
    # CSV files in extracted directories
    if extracted_dir.exists():
        for csv_file in extracted_dir.glob("**/*.csv"):
            if not csv_file.name.endswith(':Zone.Identifier'):
                csv_files.append(csv_file)
    
    logger.info(f"Found {len(csv_files)} CSV files to process (excluding cleaned folder)")
    return csv_files

def main():
    """Main function"""
    # Configuration
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "dataRaw" / "Tembici-SaoPaulo"
    output_dir = script_dir / ".." / "dataClean"
    output_file = output_dir / "consolidated_tembici_trips.csv"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Starting simple Tembici data consolidation...")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Output file: {output_file}")
    
    # Step 1: Extract ZIP files
    extracted_dir = extract_zip_files(data_dir)
    
    # Step 2: Find all CSV files (excluding cleaned folder)
    csv_files = find_csv_files(data_dir, extracted_dir)
    
    if not csv_files:
        logger.error("No CSV files found!")
        return
    
    # Step 3: Process all CSV files
    all_data = []
    
    for csv_file in csv_files:
        # Skip files in cleaned folder
        if 'cleaned' in str(csv_file):
            logger.info(f"Skipping file in cleaned folder: {csv_file}")
            continue
            
        data = process_csv_file(csv_file)
        if data:
            all_data.extend(data)
            logger.info(f"Added {len(data)} rows from {csv_file.name}")
    
    if not all_data:
        logger.error("No valid data found!")
        return
    
    # Step 4: Create final DataFrame and save
    logger.info(f"Combining {len(all_data)} total rows...")
    
    target_columns = [
        'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
        'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
        'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
    ]
    
    final_df = pd.DataFrame(all_data)
    
    # Ensure all target columns exist
    for col in target_columns:
        if col not in final_df.columns:
            final_df[col] = ''
    
    # Reorder columns to match target format
    final_df = final_df[target_columns]
    
    # Save to output file
    logger.info(f"Saving consolidated data to {output_file}")
    final_df.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"✅ SUCCESS: Consolidated {len(final_df)} rows")
    logger.info(f"Output saved to: {output_file}")
    
    # Cleanup extracted directory
    if extracted_dir.exists():
        import shutil
        shutil.rmtree(extracted_dir)
        logger.info("Cleaned up temporary extraction directory")
    
    print(f"\n✅ SUCCESS: Consolidated Tembici data saved to {output_file}")
    print(f"Total rows: {len(final_df)}")
    print(f"The file is now in the same format as userTrips.csv")

if __name__ == "__main__":
    main()