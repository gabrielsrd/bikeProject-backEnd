#!/usr/bin/env python3
"""
Tembici Data Consolidation Script

This script processes all Tembici-SaoPaulo data (ZIP files and CSV files) and consolidates
them into a single CSV file following the userTrips.csv format.

Target format (userTrips.csv):
trip_id,duration_seconds,initial_station_name,start_time,final_station_name,end_time,birth_year,initial_station_latitude,initial_station_longitude,final_station_latitude,final_station_longitude
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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TembiciDataProcessor:
    def __init__(self, data_dir, output_file):
        self.data_dir = Path(data_dir)
        self.output_file = output_file
        self.extracted_dir = self.data_dir / "extracted_temp"
        self.stations_info = {}  # Will store station coordinates
        
        # Target CSV columns
        self.target_columns = [
            'trip_id', 'duration_seconds', 'initial_station_name', 'start_time',
            'final_station_name', 'end_time', 'birth_year', 'initial_station_latitude',
            'initial_station_longitude', 'final_station_latitude', 'final_station_longitude'
        ]
        
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
                
    def load_station_coordinates(self):
        """Load station coordinates from stations files if available"""
        logger.info("Loading station coordinates...")
        
        # Look for station files in various places
        station_files = []
        
        # Check for stations in geojsons folder
        stations_geojson = self.data_dir.parent.parent / "geojsons" / "estacoes.geojson"
        if stations_geojson.exists():
            logger.info(f"Found stations geojson: {stations_geojson}")
            try:
                import json
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
                logger.info(f"Loaded {len(self.stations_info)} station coordinates from geojson")
            except Exception as e:
                logger.warning(f"Could not load station coordinates from geojson: {e}")
        
        # Look for CSV station files
        station_csv_files = list(self.data_dir.glob("**/Estações*.csv")) + list(self.data_dir.glob("**/estacoes*.csv"))
        for station_file in station_csv_files:
            try:
                logger.info(f"Loading station data from {station_file}")
                df = pd.read_csv(station_file, encoding='utf-8')
                
                # Try different column name variations
                name_cols = [col for col in df.columns if any(x in col.lower() for x in ['nome', 'name', 'station'])]
                lat_cols = [col for col in df.columns if any(x in col.lower() for x in ['lat', 'latitude'])]
                lon_cols = [col for col in df.columns if any(x in col.lower() for x in ['lon', 'longitude', 'lng'])]
                
                if name_cols and lat_cols and lon_cols:
                    for _, row in df.iterrows():
                        station_name = str(row[name_cols[0]]).strip()
                        if station_name and station_name != 'nan':
                            self.stations_info[station_name] = {
                                'latitude': float(row[lat_cols[0]]),
                                'longitude': float(row[lon_cols[0]])
                            }
                    logger.info(f"Loaded {len(self.stations_info)} total station coordinates")
                    
            except Exception as e:
                logger.warning(f"Could not load station coordinates from {station_file}: {e}")
    
    def get_station_coordinates(self, station_name):
        """Get coordinates for a station name"""
        if not station_name or pd.isna(station_name):
            return None, None
            
        station_name = str(station_name).strip()
        
        # Direct match
        if station_name in self.stations_info:
            info = self.stations_info[station_name]
            return info['latitude'], info['longitude']
        
        # Try partial matches
        for stored_name, info in self.stations_info.items():
            if station_name.lower() in stored_name.lower() or stored_name.lower() in station_name.lower():
                return info['latitude'], info['longitude']
        
        return None, None
    
    def normalize_old_format(self, df, file_path):
        """Normalize old format CSV (2018-2019) to target format"""
        logger.info(f"Processing old format file: {file_path}")
        
        normalized_data = []
        
        for idx, row in df.iterrows():
            try:
                # Generate trip_id (old format doesn't have it)
                trip_id = f"{Path(file_path).stem}_{idx}_BikeSampa"
                
                # Duration
                duration_seconds = row.get('duration_seconds', 0)
                
                # Station names
                initial_station = row.get('start_station_name', '')
                final_station = row.get('end_station_name', '')
                
                # Times (convert to ISO format)
                start_time = row.get('start_date', '')
                end_time = row.get('end_date', '')
                
                # Convert datetime format if needed - be more conservative
                if start_time and isinstance(start_time, str) and start_time.strip():
                    if not start_time.endswith('Z'):
                        try:
                            # Try to parse and convert to ISO format
                            dt = pd.to_datetime(start_time, errors='coerce')
                            if pd.notna(dt):
                                start_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        except Exception as e:
                            logger.warning(f"Could not parse datetime: {start_time}")
                            # Keep original format if parsing fails
                            pass
                        
                if end_time and isinstance(end_time, str) and end_time.strip():
                    if not end_time.endswith('Z'):
                        try:
                            # Try to parse and convert to ISO format
                            dt = pd.to_datetime(end_time, errors='coerce')
                            if pd.notna(dt):
                                end_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        except Exception as e:
                            logger.warning(f"Could not parse datetime: {end_time}")
                            # Keep original format if parsing fails
                            pass
                
                # Birth year (convert from ano_nasc) - be more careful
                birth_year = row.get('ano_nasc', '')
                if birth_year and str(birth_year) != 'nan' and str(birth_year).strip():
                    try:
                        year_int = int(float(str(birth_year)))
                        if 1900 <= year_int <= 2010:  # Reasonable birth year range
                            birth_year = f"{year_int}-01-01"
                        else:
                            birth_year = ""
                    except (ValueError, TypeError):
                        birth_year = ""
                else:
                    birth_year = ""
                
                # Get coordinates - handle safely
                init_lat, init_lon = None, None
                final_lat, final_lon = None, None
                
                try:
                    init_lat, init_lon = self.get_station_coordinates(initial_station)
                except Exception as e:
                    logger.warning(f"Error getting coordinates for initial station '{initial_station}': {e}")
                
                try:
                    final_lat, final_lon = self.get_station_coordinates(final_station)
                except Exception as e:
                    logger.warning(f"Error getting coordinates for final station '{final_station}': {e}")
                
                # Ensure duration is numeric
                try:
                    duration_seconds = int(float(duration_seconds)) if duration_seconds else 0
                except (ValueError, TypeError):
                    duration_seconds = 0
                
                normalized_row = {
                    'trip_id': trip_id,
                    'duration_seconds': duration_seconds,
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
                logger.warning(f"Error processing row {idx} in {file_path}: {e}")
                continue
        
        return pd.DataFrame(normalized_data)
    
    def normalize_new_format(self, df, file_path):
        """Normalize new format CSV (2022+) to target format"""
        logger.info(f"Processing new format file: {file_path}")
        
        # New format should already be close to target format
        normalized_data = []
        
        for idx, row in df.iterrows():
            try:
                # Most columns should map directly
                trip_id = row.get('trip_id', f"{Path(file_path).stem}_{idx}_BikeSampa")
                
                normalized_row = {
                    'trip_id': trip_id,
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
                logger.warning(f"Error processing row {idx} in {file_path}: {e}")
                continue
        
        return pd.DataFrame(normalized_data)
    
    def process_csv_file(self, file_path):
        """Process a single CSV file"""
        try:
            logger.info(f"Processing {file_path}")
            
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                logger.error(f"Could not read {file_path} with any encoding")
                return None
            
            if df.empty:
                logger.warning(f"Empty file: {file_path}")
                return None
            
            # Determine format based on columns
            columns = df.columns.tolist()
            
            if 'trip_id' in columns and 'initial_station_name' in columns:
                # New format (2022+)
                return self.normalize_new_format(df, file_path)
            elif 'start_station_name' in columns and 'duration_seconds' in columns:
                # Old format (2018-2019)
                return self.normalize_old_format(df, file_path)
            else:
                logger.warning(f"Unknown CSV format in {file_path}. Columns: {columns}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def find_all_csv_files(self):
        """Find all CSV files in data directory and extracted directories"""
        csv_files = []
        
        # CSV files in main directory
        csv_files.extend(list(self.data_dir.glob("*.csv")))
        
        # CSV files in cleaned directory
        cleaned_dir = self.data_dir / "cleaned"
        if cleaned_dir.exists():
            csv_files.extend(list(cleaned_dir.glob("*.csv")))
        
        # CSV files in extracted directories
        if self.extracted_dir.exists():
            csv_files.extend(list(self.extracted_dir.glob("**/*.csv")))
        
        # Filter out Zone.Identifier files
        csv_files = [f for f in csv_files if not f.name.endswith('.csv:Zone.Identifier')]
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        return csv_files
    
    def consolidate_data(self):
        """Main method to consolidate all data"""
        logger.info("Starting Tembici data consolidation...")
        
        # Step 1: Extract ZIP files
        self.extract_zip_files()
        
        # Step 2: Load station coordinates
        self.load_station_coordinates()
        
        # Step 3: Find all CSV files
        csv_files = self.find_all_csv_files()
        
        # Step 4: Process all CSV files
        all_dataframes = []
        
        for csv_file in csv_files:
            df = self.process_csv_file(csv_file)
            if df is not None and not df.empty:
                all_dataframes.append(df)
                logger.info(f"Added {len(df)} rows from {csv_file.name}")
        
        if not all_dataframes:
            logger.error("No valid data found!")
            return False
        
        # Step 5: Combine all dataframes
        logger.info("Combining all data...")
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Step 6: Ensure all target columns exist
        for col in self.target_columns:
            if col not in final_df.columns:
                final_df[col] = ''
        
        # Reorder columns to match target format
        final_df = final_df[self.target_columns]
        
        # Step 7: Save to output file
        logger.info(f"Saving consolidated data to {self.output_file}")
        final_df.to_csv(self.output_file, index=False, encoding='utf-8')
        
        logger.info(f"Consolidation complete! Total rows: {len(final_df)}")
        logger.info(f"Output saved to: {self.output_file}")
        
        # Cleanup
        if self.extracted_dir.exists():
            import shutil
            shutil.rmtree(self.extracted_dir)
            logger.info("Cleaned up temporary extraction directory")
        
        return True

def main():
    """Main function"""
    # Configuration
    script_dir = Path(__file__).parent
    data_dir = script_dir / "dataRaw" / "Tembici-SaoPaulo"
    output_file = script_dir / "dataClean" / "consolidated_tembici_trips.csv"
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(exist_ok=True)
    
    # Create processor and run
    processor = TembiciDataProcessor(data_dir, output_file)
    success = processor.consolidate_data()
    
    if success:
        print(f"\n✅ SUCCESS: Consolidated Tembici data saved to {output_file}")
        print(f"The file is now in the same format as userTrips.csv")
    else:
        print("\n❌ FAILED: Could not consolidate the data")

if __name__ == "__main__":
    main()