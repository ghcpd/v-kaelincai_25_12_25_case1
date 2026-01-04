"""Tests for deduplication - FIXED to be deterministic."""

import pytest
from deduplicator import deduplicate_records, generate_summary, create_report


def test_basic_deduplication():
    """Test basic deduplication functionality."""
    records = [
        {"id": "1", "name": "Alice", "city": "NYC"},
        {"id": "2", "name": "Bob", "city": "LA"},
        {"id": "1", "name": "Alice", "city": "NYC"},  # duplicate
        {"id": "3", "name": "Carol", "city": "SF"},
    ]
    
    unique_records, unique_ids = deduplicate_records(records)
    
    # Should have 3 unique records
    assert len(unique_records) == 3
    assert len(unique_ids) == 3
    
    # Should contain the right IDs in sorted order
    assert "1" in unique_ids
    assert "2" in unique_ids
    assert "3" in unique_ids
    assert unique_ids == ['1', '2', '3']


def test_summary_generation():
    """
    FIXED: Test summary string generation with deterministic output.
    
    Now that we use sorted lists instead of sets, the output is always predictable.
    """
    unique_ids = ['1', '2', '3']
    
    summary = generate_summary(unique_ids)
    
    # This assertion now always passes because the order is deterministic
    assert summary == "Unique IDs: 1, 2, 3"


def test_summary_consistency():
    """
    FIXED: Test that multiple calls produce consistent output.
    
    With sorted lists, this test is now reliable.
    """
    # Create the same sorted list multiple times
    ids1 = ['10', '20', '30']
    ids2 = ['10', '20', '30']
    ids3 = ['10', '20', '30']
    
    summary1 = generate_summary(ids1)
    summary2 = generate_summary(ids2)
    summary3 = generate_summary(ids3)
    
    # These are now guaranteed to be identical
    assert summary1 == summary2
    assert summary2 == summary3
    assert summary1 == "Unique IDs: 10, 20, 30"


def test_report_id_consistency():
    """
    FIXED: Test report ID generation consistency.
    
    Now that summaries are deterministic, report IDs are too.
    """
    records = [
        {"id": "100", "name": "Test1"},
        {"id": "200", "name": "Test2"},
        {"id": "300", "name": "Test3"},
    ]
    unique_ids = ['100', '200', '300']
    
    report1 = create_report(records, unique_ids)
    report2 = create_report(records, unique_ids)
    
    # Report IDs are now always the same for same data
    assert report1["report_id"] == report2["report_id"]
    assert report1["summary"] == report2["summary"]


def test_full_deduplication_pipeline():
    """
    FIXED: Test the full pipeline from deduplication to report.
    
    This test is now reliable with deterministic output.
    """
    records = [
        {"id": "A1", "name": "Alice", "dept": "Engineering"},
        {"id": "B2", "name": "Bob", "dept": "Sales"},
        {"id": "A1", "name": "Alice", "dept": "Engineering"},  # dup
        {"id": "C3", "name": "Carol", "dept": "Marketing"},
        {"id": "B2", "name": "Bob", "dept": "Sales"},  # dup
    ]
    
    unique_records, unique_ids = deduplicate_records(records)
    report = create_report(unique_records, unique_ids)
    
    # These assertions now always pass
    assert report["total_unique"] == 3
    assert len(report["records"]) == 3
    
    # The summary string order is now deterministic (sorted)
    expected_summary = "Unique IDs: A1, B2, C3"
    assert report["summary"] == expected_summary


def test_deterministic_with_multiple_runs():
    """
    Test that running deduplication multiple times produces identical results.
    """
    records = [
        {"id": "Z9", "name": "Zoe"},
        {"id": "A1", "name": "Alice"},
        {"id": "M5", "name": "Mike"},
        {"id": "A1", "name": "Alice"},  # dup
    ]
    
    # Run multiple times
    results = []
    for _ in range(10):
        unique_records, unique_ids_list = deduplicate_records(records)
        summary = generate_summary(unique_ids_list)
        results.append(summary)
    
    # All results should be identical
    first_summary = results[0]
    for summary in results[1:]:
        assert summary == first_summary
    
    # Should be sorted
    assert first_summary == "Unique IDs: A1, M5, Z9"


def test_report_consistency():
    """
    Test that report generation is deterministic.
    """
    records = [
        {"id": "30", "name": "Test"},
        {"id": "10", "name": "Test"},
        {"id": "20", "name": "Test"},
    ]
    
    unique_records, unique_ids_list = deduplicate_records(records)
    
    reports = []
    for _ in range(5):
        report = create_report(unique_records, unique_ids_list)
        reports.append(report)
    
    # All reports should have identical IDs
    first_id = reports[0]["report_id"]
    for report in reports[1:]:
        assert report["report_id"] == first_id
    
    # All summaries should be identical
    first_summary = reports[0]["summary"]
    for report in reports[1:]:
        assert report["summary"] == first_summary
    
    # Summary should be sorted
    assert first_summary == "Unique IDs: 10, 20, 30"


def test_summary_with_unsorted_input():
    """
    Test that even with unsorted IDs, the deduplication produces sorted output.
    """
    ids = ["5", "3", "1", "4", "2"]
    
    # Simulate deduplication with unsorted IDs
    records = [{"id": id, "name": f"Person{id}"} for id in ids]
    unique_records, unique_ids = deduplicate_records(records)
    
    # Should be sorted
    assert unique_ids == ["1", "2", "3", "4", "5"]
    
    summary = generate_summary(unique_ids)
    assert summary == "Unique IDs: 1, 2, 3, 4, 5"
