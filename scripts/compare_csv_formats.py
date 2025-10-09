#!/usr/bin/env python3
"""
Quick CSV format comparison script
"""

import csv
from pathlib import Path

def compare_csv_formats():
    """Compare the headers and sample data of both CSV files"""
    
    usertrips_file = Path("dataRaw/userTrips.csv")
    consolidated_file = Path("dataClean/consolidated_tembici_trips.csv")
    
    print("="*80)
    print("CSV FORMAT COMPARISON")
    print("="*80)
    
    # Check userTrips.csv
    print("\n1. ORIGINAL userTrips.csv:")
    with open(usertrips_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header1 = next(reader)
        sample1 = next(reader)
    
    print(f"   Columns ({len(header1)}): {header1}")
    print(f"   Sample data: {sample1}")
    
    # Check consolidated file
    print("\n2. CONSOLIDATED consolidated_tembici_trips.csv:")
    with open(consolidated_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header2 = next(reader)
        sample2 = next(reader)
    
    print(f"   Columns ({len(header2)}): {header2}")
    print(f"   Sample data: {sample2}")
    
    # Compare headers
    print(f"\n3. COMPARISON:")
    if header1 == header2:
        print("   ✅ Headers match perfectly!")
    else:
        print("   ❌ Headers don't match!")
        print(f"   Original: {header1}")
        print(f"   Consolidated: {header2}")
    
    # Check file sizes
    import os
    size1 = os.path.getsize(usertrips_file)
    size2 = os.path.getsize(consolidated_file)
    
    print(f"\n4. FILE SIZES:")
    print(f"   userTrips.csv: {size1:,} bytes ({size1/1024/1024:.1f} MB)")
    print(f"   consolidated_tembici_trips.csv: {size2:,} bytes ({size2/1024/1024:.1f} MB)")
    
    # Count rows
    with open(usertrips_file, 'r', encoding='utf-8') as f:
        rows1 = sum(1 for line in f) - 1  # minus header
    
    with open(consolidated_file, 'r', encoding='utf-8') as f:
        rows2 = sum(1 for line in f) - 1  # minus header
    
    print(f"\n5. ROW COUNTS:")
    print(f"   userTrips.csv: {rows1:,} rows")
    print(f"   consolidated_tembici_trips.csv: {rows2:,} rows")
    print(f"   Ratio: {rows2/rows1:.1f}x more data in consolidated file")

if __name__ == "__main__":
    compare_csv_formats()