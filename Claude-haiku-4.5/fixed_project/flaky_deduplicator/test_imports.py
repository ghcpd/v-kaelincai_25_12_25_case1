"""Test module imports and functionality."""

import sys
sys.path.insert(0, 'src')

print("Testing module imports...")
try:
    from deduplicator import deduplicate_records, generate_summary, create_report, process_csv
    print("✅ All module imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\nTesting function signatures...")
try:
    # Test basic deduplication
    records = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "name": "Alice"},  # duplicate
    ]
    
    unique_records, unique_ids = deduplicate_records(records)
    assert isinstance(unique_ids, list), "unique_ids should be a list"
    assert unique_ids == ["1", "2"], f"Expected ['1', '2'], got {unique_ids}"
    print("✅ deduplicate_records() returns sorted list")
    
    # Test summary generation
    summary = generate_summary(unique_ids)
    assert isinstance(summary, str), "summary should be a string"
    assert summary == "Unique IDs: 1, 2", f"Expected 'Unique IDs: 1, 2', got '{summary}'"
    print("✅ generate_summary() works correctly")
    
    # Test report creation
    report = create_report(unique_records, unique_ids)
    assert isinstance(report, dict), "report should be a dict"
    assert "report_id" in report, "report should have report_id"
    assert "summary" in report, "report should have summary"
    assert "total_unique" in report, "report should have total_unique"
    print("✅ create_report() works correctly")
    
    print("\n✅ All functionality tests passed!")
    
except AssertionError as e:
    print(f"❌ Assertion failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
