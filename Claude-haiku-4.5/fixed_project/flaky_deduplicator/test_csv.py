"""Test CSV processing functionality."""

import sys
import os
sys.path.insert(0, 'src')

from deduplicator import process_csv

print("=== TESTING CSV PROCESSING FUNCTIONALITY ===\n")

csv_file = 'data/sample_data.csv'

if not os.path.exists(csv_file):
    print(f"❌ CSV file not found: {csv_file}")
    sys.exit(1)

print(f"Reading CSV file: {csv_file}")

try:
    # Process CSV file
    unique_records, unique_ids = process_csv(csv_file)
    
    print(f"\n✅ CSV file processed successfully")
    print(f"   - Total unique records: {len(unique_records)}")
    print(f"   - Unique IDs: {unique_ids}")
    
    # Verify it returns a list
    assert isinstance(unique_ids, list), "unique_ids should be a list"
    print(f"✅ unique_ids is a list (not a set)")
    
    # Verify it's sorted
    assert unique_ids == sorted(unique_ids), "unique_ids should be sorted"
    print(f"✅ unique_ids are sorted")
    
    # Expected IDs from sample data
    expected_ids = ['1', '2', '3', '4', '5', '6']
    assert unique_ids == expected_ids, f"Expected {expected_ids}, got {unique_ids}"
    print(f"✅ Correct unique IDs extracted from CSV")
    
    print("\n✅ All CSV processing tests passed!")
    
    # Print sample records
    print(f"\nSample records (first 3):")
    for i, record in enumerate(unique_records[:3], 1):
        print(f"  {i}. {record}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
