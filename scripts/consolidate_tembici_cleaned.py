#!/usr/bin/env python3
"""
Consolidate Tembici Data (2018-2023)
Process ZIP files and CSV files from dataRaw/Tembici-SaoPaulo/
Includes data from 2018-2023 (excluding old 'cleaned' folder)
"""

import pandas as pd
import glob
import zipfile
import tempfile
import os
from pathlib import Path
from datetime import datetime
import sys

def consolidate_cleaned_data():
    print("=" * 70)
    print("🚀 Consolidating Tembici Data (2018-2023)")
    print("=" * 70)
    
    # Path to Tembici-SaoPaulo folder
    base_path = Path(__file__).parent.parent
    tembici_folder = base_path / "dataRaw/Tembici-SaoPaulo"
    
    # Get all ZIP files (excluding Zone.Identifier files)
    zip_files = sorted([f for f in tembici_folder.glob("*.zip") 
                       if not f.name.endswith(':Zone.Identifier')])
    
    # Get CSV files directly in the folder (not in 'cleaned' subfolder)
    csv_files = sorted([f for f in tembici_folder.glob("*.csv") 
                       if not f.name.endswith(':Zone.Identifier')])
    
    if not zip_files and not csv_files:
        print(f"❌ No ZIP or CSV files found in: {tembici_folder}")
        print("Please check if the path is correct.")
        sys.exit(1)
    
    print(f"\n� Found {len(zip_files)} ZIP files to process")
    print(f"📄 Found {len(csv_files)} CSV files to process")
    print(f"📁 Source folder: {tembici_folder}")
    print()
    
    all_data = []
    total_rows = 0
    errors = 0
    file_count = 0
    
    # Process ZIP files first
    for zip_idx, zip_file in enumerate(zip_files, 1):
        print(f"[ZIP {zip_idx:2d}/{len(zip_files)}] Processing: {zip_file.name}...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Extract all files
                    zip_ref.extractall(temp_dir)
                
                # Find all CSV files in extracted content
                temp_path = Path(temp_dir)
                extracted_csvs = list(temp_path.glob("**/*.csv"))
                
                print(f"   Found {len(extracted_csvs)} CSV files inside ZIP")
                
                for csv_file in extracted_csvs:
                    file_count += 1
                    csv_name = csv_file.name
                    
                    # Skip if filename doesn't contain 'trip' or 'BikeSampa'
                    if 'trip' not in csv_name.lower() and 'bikesampa' not in csv_name.lower():
                        print(f"   ⏭️  Skipping non-trip file: {csv_name}")
                        continue
                    
                    print(f"   [{file_count}] {csv_name}...", end=" ")
                    
                    data = process_csv_file(csv_file)
                    if data is not None:
                        all_data.append(data)
                        total_rows += len(data)
                        print(f"✅ {len(data):,} rows")
                    else:
                        errors += 1
        
        except Exception as e:
            print(f"   ❌ Error processing ZIP: {e}")
            errors += 1
            continue
    
    # Process loose CSV files
    print(f"\n📄 Processing loose CSV files...")
    for idx, csv_file in enumerate(csv_files, 1):
        file_count += 1
        file_name = csv_file.name
        print(f"[CSV {idx:2d}/{len(csv_files)}] {file_name}...", end=" ")
        
        data = process_csv_file(csv_file)
        if data is not None:
            all_data.append(data)
            total_rows += len(data)
            print(f"✅ {len(data):,} rows")
        else:
            errors += 1
    
    # Consolidate all data
    if all_data:
        print("\n" + "=" * 70)
        print("📊 Consolidating all data...")
        consolidated = pd.concat(all_data, ignore_index=True)
        
        # Generate output filename with timestamp
        output_file = base_path / "dataRaw/consolidated_tembici_data.csv"
        
        print(f"💾 Writing {len(consolidated):,} rows to:")
        print(f"   {output_file}")
        
        # Save to CSV
        consolidated.to_csv(output_file, index=False, encoding='utf-8')
        
        # Get file size
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        
        print("\n" + "=" * 70)
        print("✅ CONSOLIDATION COMPLETE!")
        print("=" * 70)
        print(f"📄 Output file: {output_file.name}")
        print(f"📊 Total records: {len(consolidated):,}")
        print(f"💾 File size: {file_size_mb:.1f} MB")
        print(f"✅ Successful files: {len(csv_files) - errors}")
        if errors > 0:
            print(f"⚠️  Failed files: {errors}")
        
        # Show column info
        print("\n📋 Column summary:")
        for col in consolidated.columns:
            non_null = consolidated[col].notna().sum()
            print(f"   {col:30s}: {non_null:,} non-null values")
        
        # Show sample data
        print("\n📝 First 3 records:")
        print("-" * 70)
        for i in range(min(3, len(consolidated))):
            print(f"\nRecord {i+1}:")
            for col in consolidated.columns:
                val = consolidated.iloc[i][col]
                if val != '':
                    print(f"  {col:30s}: {val}")
        
        print("\n" + "=" * 70)
        print("🎉 You can now import this file to the database with:")
        print(f"   python3 manage.py import_trips dataRaw/consolidated_tembici_data.csv")
        print("=" * 70)
        
        return True
        
    else:
        print("\n" + "=" * 70)
        print("❌ ERROR: No data to consolidate!")
        print("=" * 70)
        return False

def process_csv_file(csv_file):
    """Process a single CSV file and normalize to target format"""
    try:
        # Try different encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
            try:
                df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        
        if df is None or len(df) == 0:
            print(f"❌ Could not read file")
            return None
        
        # Normalize column names (lowercase, strip spaces)
        df.columns = df.columns.str.lower().str.strip()
        
        # Check what format this CSV is in
        # Format 1: New format (2021-2023) - already has correct columns
        if 'trip_id' in df.columns and 'initial_station_name' in df.columns and 'start_time' in df.columns:
            # Already in correct format!
            df_normalized = df[[
                'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
                'final_station_name', 'end_time', 'birth_year',
                'initial_station_latitude', 'initial_station_longitude',
                'final_station_latitude', 'final_station_longitude'
            ]].copy()
            
        # Format 2: Old format (2018-2020) - needs mapping
        elif 'start_station_name' in df.columns and 'start_date' in df.columns:
            df_normalized = pd.DataFrame({
                'trip_id': [f"{Path(csv_file).stem}_{i}" for i in range(len(df))],
                'duration_seconds': df['duration_seconds'],
                'initial_station_name': df['start_station_name'],
                'start_time': df['start_date'],
                'final_station_name': df['end_station_name'],
                'end_time': df['end_date'],
                'birth_year': df.get('ano_nasc', ''),
                'initial_station_latitude': df.get('initial_station_latitude', ''),
                'initial_station_longitude': df.get('initial_station_longitude', ''),
                'final_station_latitude': df.get('final_station_latitude', ''),
                'final_station_longitude': df.get('final_station_longitude', '')
            })
        else:
            print(f"❌ Unknown format. Columns: {list(df.columns)[:5]}")
            return None
        
        return df_normalized
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    try:
        success = consolidate_cleaned_data()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
