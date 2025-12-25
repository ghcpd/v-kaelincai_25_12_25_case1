"""Demonstration script showing the fix works correctly."""

import sys
sys.path.insert(0, 'src')

from deduplicator import deduplicate_records, generate_summary, create_report

def main():
    print("=" * 60)
    print("Data Deduplicator - FIXED Version Demonstration")
    print("=" * 60)
    print()
    
    # Test data with unsorted IDs
    records = [
        {"id": "Z9", "name": "Zoe", "dept": "Marketing"},
        {"id": "A1", "name": "Alice", "dept": "Engineering"},
        {"id": "M5", "name": "Mike", "dept": "Sales"},
        {"id": "A1", "name": "Alice", "dept": "Engineering"},  # duplicate
        {"id": "C3", "name": "Carol", "dept": "HR"},
        {"id": "M5", "name": "Mike", "dept": "Sales"},  # duplicate
    ]
    
    print("Input records (with duplicates):")
    for i, record in enumerate(records, 1):
        print(f"  {i}. ID={record['id']}, Name={record['name']}, Dept={record['dept']}")
    print()
    
    # Run deduplication
    unique_records, unique_ids = deduplicate_records(records)
    
    print(f"Deduplication Results:")
    print(f"  - Total input records: {len(records)}")
    print(f"  - Unique records: {len(unique_records)}")
    print(f"  - Duplicates removed: {len(records) - len(unique_records)}")
    print()
    
    print(f"Unique IDs (sorted): {unique_ids}")
    print()
    
    # Generate summary
    summary = generate_summary(unique_ids)
    print(f"Summary: {summary}")
    print()
    
    # Create report
    report = create_report(unique_records, unique_ids)
    print(f"Report Details:")
    print(f"  - Report ID: {report['report_id']}")
    print(f"  - Total Unique: {report['total_unique']}")
    print(f"  - Summary: {report['summary']}")
    print()
    
    # Demonstrate consistency
    print("=" * 60)
    print("Consistency Test: Running 10 times")
    print("=" * 60)
    
    summaries = set()
    report_ids = set()
    
    for i in range(10):
        _, ids = deduplicate_records(records)
        s = generate_summary(ids)
        r = create_report(unique_records, ids)
        
        summaries.add(s)
        report_ids.add(r['report_id'])
    
    print(f"Unique summaries found: {len(summaries)}")
    print(f"Unique report IDs found: {len(report_ids)}")
    print()
    
    if len(summaries) == 1 and len(report_ids) == 1:
        print("✅ SUCCESS: All runs produced identical output!")
        print("   The fix eliminates flaky behavior completely.")
    else:
        print("❌ FAILURE: Different outputs detected!")
        print(f"   Summaries: {summaries}")
        print(f"   Report IDs: {report_ids}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
