import csv
import os

def check_files():
    # Check userTrips.csv
    print("=== userTrips.csv ===")
    usertrips_path = "dataRaw/userTrips.csv"
    if os.path.exists(usertrips_path):
        with open(usertrips_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header1 = next(reader)
            sample1 = next(reader)
        print(f"Columns ({len(header1)}): {header1}")
        print(f"Size: {os.path.getsize(usertrips_path) / 1024 / 1024:.1f} MB")
        
    # Check consolidated file
    print("\n=== consolidated_tembici_trips.csv ===")
    consolidated_path = "dataClean/consolidated_tembici_trips.csv"
    if os.path.exists(consolidated_path):
        with open(consolidated_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header2 = next(reader)
            sample2 = next(reader)
        print(f"Columns ({len(header2)}): {header2}")
        print(f"Size: {os.path.getsize(consolidated_path) / 1024 / 1024:.1f} MB")
        
        # Compare
        print(f"\n=== COMPARISON ===")
        if header1 == header2:
            print("✅ Headers match perfectly!")
        else:
            print("❌ Headers don't match")
    
check_files()