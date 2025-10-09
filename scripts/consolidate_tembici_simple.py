#!/usr/bin/env python3
"""
Simple Tembici Data Consolidation Script

This script processes Tembici-SaoPaulo data (ZIP files and CSV files) and consolidates
them into a single CSV file following the userTrips.csv format.
Ignores the cleaned folder and processes raw data directly.
"""

import os
import csv
import zipfile
import pandas as pd
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

def parse_datetime(date_str):
    """Parse various datetime formats found in Tembici data"""
    if pd.isna(date_str) or not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Common formats in Tembici data
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%d/%m/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    print(f"Warning: Could not parse datetime: {date_str}")
    return None

def process_csv_file(file_path):
    """Process a single CSV file and normalize to target format"""
    print(f"Processing CSV: {file_path}")
    
    try:
        # Try different encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"Could not read {file_path} with any encoding")
            return []
        
        print(f"Loaded {len(df)} rows from {file_path}")
        print(f"Columns: {list(df.columns)}")
        
        normalized_data = []
        
        # Detect format based on columns
        columns = [col.lower().strip() for col in df.columns]
        
        for idx, row in df.iterrows():
            try:
                # Generate trip_id if not present
                if 'trip_id' in columns:
                    trip_id = row.get('trip_id') or row.get('Trip ID') or f"{Path(file_path).stem}_{idx}"
                else:
                    trip_id = f"{Path(file_path).stem}_{idx}"
                
                # Duration
                duration_seconds = 0
                for dur_col in ['duration_seconds', 'tripduration', 'duration']:
                    if dur_col in columns:
                        duration_seconds = row.get(dur_col, 0)
                        break
                
                # Station names
                initial_station = ""
                final_station = ""
                
                for start_col in ['start_station_name', 'initial_station_name', 'from_station_name']:
                    if start_col in columns:
                        initial_station = row.get(start_col, "")
                        break
                
                for end_col in ['end_station_name', 'final_station_name', 'to_station_name']:
                    if end_col in columns:
                        final_station = row.get(end_col, "")
                        break
                
                # Times
                start_time = ""
                end_time = ""
                
                for start_time_col in ['starttime', 'start_time', 'initial_time']:
                    if start_time_col in columns:
                        dt = parse_datetime(row.get(start_time_col))
                        if dt:
                            start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        break
                
                for end_time_col in ['stoptime', 'end_time', 'final_time']:
                    if end_time_col in columns:
                        dt = parse_datetime(row.get(end_time_col))
                        if dt:
                            end_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        break
                
                # Birth year
                birth_year = ""
                for birth_col in ['birth_year', 'birth year', 'user_birth_year']:
                    if birth_col in columns:
                        birth_year = row.get(birth_col, "")
                        break
                
                # Coordinates (often not available in source data)
                initial_lat = row.get('start_station_latitude', "") or row.get('initial_station_latitude', "")
                initial_lon = row.get('start_station_longitude', "") or row.get('initial_station_longitude', "")
                final_lat = row.get('end_station_latitude', "") or row.get('final_station_latitude', "")
                final_lon = row.get('end_station_longitude', "") or row.get('final_station_longitude', "")
                
                normalized_row = {
                    'trip_id': trip_id,
                    'duration_seconds': duration_seconds,
                    'initial_station_name': initial_station,
                    'start_time': start_time,
                    'final_station_name': final_station,
                    'end_time': end_time,
                    'birth_year': birth_year,
                    'initial_station_latitude': initial_lat,
                    'initial_station_longitude': initial_lon,
                    'final_station_latitude': final_lat,
                    'final_station_longitude': final_lon
                }
                
                normalized_data.append(normalized_row)
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        print(f"Successfully processed {len(normalized_data)} rows from {file_path}")
        return normalized_data
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def process_zip_file(zip_path):
    """Extract and process CSV files from a ZIP file"""
    print(f"Processing ZIP: {zip_path}")
    
    all_data = []
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find all CSV files in the extracted content
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.csv'):
                        csv_path = os.path.join(root, file)
                        data = process_csv_file(csv_path)
                        all_data.extend(data)
    
    except Exception as e:
        print(f"Error processing ZIP {zip_path}: {e}")
    
    return all_data

def consolidate_tembici_data(source_folder, output_file):
    """Main function to consolidate all Tembici data"""
    print(f"Consolidating Tembici data from: {source_folder}")
    print(f"Output file: {output_file}")
    
    all_data = []
    processed_files = []
    
    source_path = Path(source_folder)
    
    # Process loose CSV files first (ignoring cleaned folder)
    for file_path in source_path.glob("*.csv"):
        if not str(file_path).endswith(':Zone.Identifier'):
            data = process_csv_file(file_path)
            if data:
                all_data.extend(data)
                processed_files.append(file_path.name)
    
    # Process ZIP files (ignoring cleaned folder)
    for file_path in source_path.glob("*.zip"):
        if not str(file_path).endswith(':Zone.Identifier'):
            data = process_zip_file(file_path)
            if data:
                all_data.extend(data)
                processed_files.append(file_path.name)
    
    # Write consolidated data
    if all_data:
        print(f"\nWriting {len(all_data)} total records to {output_file}")
        
        # Define the target columns
        target_columns = [
            'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
            'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
            'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=target_columns)
            writer.writeheader()
            writer.writerows(all_data)
        
        print(f"Successfully created consolidated file: {output_file}")
        print(f"Processed files: {processed_files}")
        
        # Print sample of the data
        print(f"\nFirst 3 records:")
        for i, record in enumerate(all_data[:3]):
            print(f"Record {i+1}: {record}")
            
    else:
        print("No data found to consolidate!")

if __name__ == "__main__":
    # Default paths
    source_folder = "/home/galves/gabriel/usp/tccBike/bikeProject-backEnd/dataRaw/Tembici-SaoPaulo"
    output_file = "/home/galves/gabriel/usp/tccBike/bikeProject-backEnd/dataRaw/consolidated_tembici_data.csv"
    
    consolidate_tembici_data(source_folder, output_file)