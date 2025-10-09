#!/usr/bin/env python3
"""
Tembici CSV Header Inspector

This script examines all CSV files and shows their headers to understand
the different formats before consolidation.
"""

import pandas as pd
import logging
from pathlib import Path
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def examine_csv_headers(data_dir):
    """Examine headers of all CSV files and group by format"""
    data_path = Path(data_dir)
    
    # Find all CSV files
    csv_files = []
    
    # CSV files in main directory
    main_csvs = [f for f in data_path.glob("*.csv") if not f.name.endswith(':Zone.Identifier')]
    csv_files.extend(main_csvs)
    
    # CSV files in extracted directory
    extracted_dir = data_path / "extracted"
    if extracted_dir.exists():
        extracted_csvs = [f for f in extracted_dir.glob("**/*.csv") if not f.name.endswith(':Zone.Identifier')]
        csv_files.extend(extracted_csvs)
    
    logger.info(f"Found {len(csv_files)} CSV files to examine")
    
    # Group files by their column headers
    header_groups = defaultdict(list)
    file_info = []
    
    for csv_file in csv_files:
        try:
            # Read just the header and first few rows
            df_sample = pd.read_csv(csv_file, nrows=3, encoding='utf-8')
            columns_tuple = tuple(sorted(df_sample.columns))
            header_groups[columns_tuple].append(csv_file)
            
            file_info.append({
                'file': csv_file,
                'columns': list(df_sample.columns),
                'rows': len(df_sample),
                'sample_data': df_sample.iloc[0].to_dict() if not df_sample.empty else {}
            })
            
        except Exception as e:
            logger.error(f"Error reading {csv_file}: {e}")
            continue
    
    # Show results
    print("\n" + "="*80)
    print("CSV FILE HEADER ANALYSIS")
    print("="*80)
    
    target_format = [
        'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
        'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
        'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
    ]
    
    print(f"\nTARGET FORMAT (userTrips.csv):")
    print(f"Columns: {target_format}")
    
    format_counter = 1
    for columns_tuple, files in header_groups.items():
        columns = list(columns_tuple)
        print(f"\n{'='*60}")
        print(f"FORMAT #{format_counter} ({len(files)} files)")
        print(f"{'='*60}")
        print(f"Columns: {columns}")
        
        # Show sample files
        print(f"\nSample files:")
        for file in files[:5]:  # Show first 5 files
            print(f"  - {file.name}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
        
        # Show sample data
        sample_file_info = next((info for info in file_info if info['file'] in files), None)
        if sample_file_info and sample_file_info['sample_data']:
            print(f"\nSample data from {sample_file_info['file'].name}:")
            for key, value in list(sample_file_info['sample_data'].items())[:5]:
                print(f"  {key}: {value}")
        
        # Analyze compatibility with target format
        print(f"\nCompatibility analysis:")
        matching_cols = set(columns) & set(target_format)
        missing_cols = set(target_format) - set(columns)
        extra_cols = set(columns) - set(target_format)
        
        print(f"  Matching columns: {len(matching_cols)}/{len(target_format)}")
        if matching_cols:
            print(f"    {sorted(matching_cols)}")
        
        if missing_cols:
            print(f"  Missing columns: {sorted(missing_cols)}")
        
        if extra_cols:
            print(f"  Extra columns: {sorted(extra_cols)}")
        
        format_counter += 1
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total CSV files: {len(csv_files)}")
    print(f"Different formats found: {len(header_groups)}")
    
    # Suggest mapping strategy
    print(f"\nSUGGESTED MAPPING STRATEGY:")
    print(f"Based on the analysis above, we can create format mappings for:")
    
    for i, (columns_tuple, files) in enumerate(header_groups.items(), 1):
        columns = list(columns_tuple)
        print(f"\nFormat #{i}: {len(files)} files")
        
        # Suggest mappings based on common patterns
        suggestions = {}
        
        for target_col in target_format:
            # Look for exact matches first
            if target_col in columns:
                suggestions[target_col] = target_col
            else:
                # Look for similar column names
                for col in columns:
                    col_lower = col.lower()
                    target_lower = target_col.lower()
                    
                    if target_col == 'trip_id' and any(x in col_lower for x in ['id', 'recorrido']):
                        suggestions[target_col] = col
                    elif target_col == 'duration_seconds' and any(x in col_lower for x in ['duration', 'duracion']):
                        suggestions[target_col] = col
                    elif target_col == 'initial_station_name' and any(x in col_lower for x in ['start_station', 'nombre_estacion_origen']):
                        suggestions[target_col] = col
                    elif target_col == 'final_station_name' and any(x in col_lower for x in ['end_station', 'nombre_estacion_destino']):
                        suggestions[target_col] = col
                    elif target_col == 'start_time' and any(x in col_lower for x in ['start_date', 'fecha_origen']):
                        suggestions[target_col] = col
                    elif target_col == 'end_time' and any(x in col_lower for x in ['end_date', 'fecha_destino']):
                        suggestions[target_col] = col
                    elif target_col == 'birth_year' and any(x in col_lower for x in ['ano_nasc', 'birth']):
                        suggestions[target_col] = col
                    elif 'latitude' in target_col and any(x in col_lower for x in ['lat']):
                        if 'initial' in target_col and 'origen' in col_lower:
                            suggestions[target_col] = col
                        elif 'final' in target_col and 'destino' in col_lower:
                            suggestions[target_col] = col
                    elif 'longitude' in target_col and any(x in col_lower for x in ['lon', 'lng']):
                        if 'initial' in target_col and 'origen' in col_lower:
                            suggestions[target_col] = col
                        elif 'final' in target_col and 'destino' in col_lower:
                            suggestions[target_col] = col
        
        print(f"  Suggested mappings:")
        for target_col, source_col in suggestions.items():
            print(f"    {target_col} <- {source_col}")
        
        missing = set(target_format) - set(suggestions.keys())
        if missing:
            print(f"  Missing (will be empty): {sorted(missing)}")

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "dataRaw" / "Tembici-SaoPaulo"
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    examine_csv_headers(data_dir)

if __name__ == "__main__":
    main()