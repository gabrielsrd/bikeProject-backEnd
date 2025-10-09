#!/usr/bin/env python3
"""
Tembici Data Extractor

This script extracts all ZIP files in the Tembici-SaoPaulo folder and organizes the extracted CSV files.
"""

import os
import zipfile
import logging
from pathlib import Path
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_tembici_data(data_dir):
    """Extract all ZIP files in the Tembici-SaoPaulo directory"""
    data_path = Path(data_dir)
    extracted_dir = data_path / "extracted"
    
    # Create extraction directory
    extracted_dir.mkdir(exist_ok=True)
    
    # Find all ZIP files
    zip_files = list(data_path.glob("*.zip"))
    logger.info(f"Found {len(zip_files)} ZIP files to extract")
    
    if not zip_files:
        logger.warning("No ZIP files found!")
        return False
    
    extracted_count = 0
    
    for zip_file in zip_files:
        # Skip Zone.Identifier files
        if zip_file.name.endswith(':Zone.Identifier'):
            continue
            
        try:
            logger.info(f"Extracting {zip_file.name}...")
            
            # Create subdirectory for this zip
            extract_subdir = extracted_dir / zip_file.stem
            extract_subdir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_subdir)
                
            # Count CSV files in extracted directory
            csv_files = list(extract_subdir.glob("**/*.csv"))
            logger.info(f"  ✓ Extracted {len(csv_files)} CSV files to {extract_subdir.name}")
            extracted_count += 1
            
        except Exception as e:
            logger.error(f"  ✗ Error extracting {zip_file.name}: {e}")
            continue
    
    logger.info(f"\n✅ Extraction complete!")
    logger.info(f"Successfully extracted {extracted_count}/{len(zip_files)} ZIP files")
    logger.info(f"Extracted files are in: {extracted_dir}")
    
    # List all CSV files found
    all_csv_files = list(extracted_dir.glob("**/*.csv"))
    non_zone_csv_files = [f for f in all_csv_files if not f.name.endswith(':Zone.Identifier')]
    
    logger.info(f"Total CSV files extracted: {len(non_zone_csv_files)}")
    
    # Show structure
    logger.info("\nExtracted structure:")
    for subdir in sorted(extracted_dir.glob("*")):
        if subdir.is_dir():
            csv_count = len([f for f in subdir.glob("**/*.csv") if not f.name.endswith(':Zone.Identifier')])
            logger.info(f"  {subdir.name}: {csv_count} CSV files")
    
    return True

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    data_dir = script_dir / ".." / "dataRaw" / "Tembici-SaoPaulo"
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    logger.info(f"Starting extraction from: {data_dir}")
    success = extract_tembici_data(data_dir)
    
    if success:
        print(f"\n✅ SUCCESS: All ZIP files extracted!")
        print(f"Next step: Run the consolidation script to merge CSV files")
    else:
        print(f"\n❌ FAILED: Could not extract ZIP files")

if __name__ == "__main__":
    main()