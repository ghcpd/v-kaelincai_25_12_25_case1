"""Tests for deduplication - demonstrates flaky behavior."""

import pytest
from deduplicator import deduplicate_records, generate_summary, create_report
from deduplicator.deduplicator import deduplicate_records_fixed
from deduplicator.reporter import generate_summary_fixed, create_report_fixed


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
    
    # Should contain the right IDs
    assert "1" in unique_ids
    assert "2" in unique_ids
    assert "3" in unique_ids


def test_summary_generation():
    """
    FLAKY TEST: Test summary string generation.
    
    This test will be FLAKY because it depends on set iteration order.
    The same set can produce different string outputs in different runs.
    
    Expected behavior:
    - Run in same process: usually passes (same hash seed)
    - Run in new process: may fail (different hash seed)
    - Run multiple times with pytest-randomly: fails frequently
    """
    unique_ids = {"3", "1", "2"}
    
    summary = generate_summary(unique_ids)
    
    # This assertion may fail! The order of IDs in the string is undefined.
    # Possible outputs: "1, 2, 3" or "2, 3, 1" or "3, 1, 2" etc.
    assert summary == "Unique IDs: 1, 2, 3", \
        f"Expected 'Unique IDs: 1, 2, 3' but got '{summary}'"


def test_summary_consistency():
    """
    FLAKY TEST: Test that multiple calls produce consistent output.
    
    This test demonstrates the bug: even calling the same function
    multiple times within the same test may produce different results
    if the set is recreated each time.
    """
    # Create the same set multiple times
    ids1 = {"10", "20", "30"}
    ids2 = {"10", "20", "30"}
    ids3 = {"10", "20", "30"}
    
    summary1 = generate_summary(ids1)
    summary2 = generate_summary(ids2)
    summary3 = generate_summary(ids3)
    
    # These should be identical, but may not be!
    # Within same process they usually are, but not guaranteed
    assert summary1 == summary2, \
        f"Inconsistent summaries: '{summary1}' != '{summary2}'"
    assert summary2 == summary3, \
        f"Inconsistent summaries: '{summary2}' != '{summary3}'"


def test_report_id_consistency():
    """
    FLAKY TEST: Test report ID generation consistency.
    
    The report ID is generated based on a hash of the summary string.
    Since the summary depends on set iteration order, the report ID
    will be different across runs.
    """
    records = [
        {"id": "100", "name": "Test1"},
        {"id": "200", "name": "Test2"},
        {"id": "300", "name": "Test3"},
    ]
    unique_ids = {"100", "200", "300"}
    
    report1 = create_report(records, unique_ids)
    report2 = create_report(records, unique_ids)
    
    # Report IDs should be the same for same data
    # But they may differ due to set iteration order!
    assert report1["report_id"] == report2["report_id"], \
        f"Inconsistent report IDs: {report1['report_id']} != {report2['report_id']}"


def test_full_deduplication_pipeline():
    """
    FLAKY TEST: Test the full pipeline from deduplication to report.
    
    This test will be flaky because the report generation depends
    on the set iteration order.
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
    
    # These assertions should pass
    assert report["total_unique"] == 3
    assert len(report["records"]) == 3
    
    # This assertion is FLAKY - the summary string order is undefined
    expected_summary = "Unique IDs: A1, B2, C3"
    assert report["summary"] == expected_summary, \
        f"Expected '{expected_summary}' but got '{report['summary']}'"


def test_fixed_version_is_deterministic():
    """
    Test the FIXED version with sorted lists.
    
    This test should ALWAYS PASS because the fixed version
    uses sorted lists instead of sets.
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
        unique_records, unique_ids_list = deduplicate_records_fixed(records)
        summary = generate_summary_fixed(unique_ids_list)
        results.append(summary)
    
    # All results should be identical
    first_summary = results[0]
    for summary in results[1:]:
        assert summary == first_summary, \
            f"Fixed version should be deterministic!"
    
    # Should be sorted
    assert first_summary == "Unique IDs: A1, M5, Z9"


def test_fixed_report_consistency():
    """
    Test that the fixed report generation is deterministic.
    """
    records = [
        {"id": "30", "name": "Test"},
        {"id": "10", "name": "Test"},
        {"id": "20", "name": "Test"},
    ]
    
    # Use fixed version
    unique_records, unique_ids_list = deduplicate_records_fixed(records)
    
    reports = []
    for _ in range(5):
        report = create_report_fixed(unique_records, unique_ids_list)
        reports.append(report)
    
    # All reports should have identical IDs
    first_id = reports[0]["report_id"]
    for report in reports[1:]:
        assert report["report_id"] == first_id
    
    # All summaries should be identical
    first_summary = reports[0]["summary"]
    for report in reports[1:]:
        assert report["summary"] == first_summary


@pytest.mark.xfail(reason="Known flaky test due to set iteration order")
def test_known_flaky_summary():
    """
    This test is marked as expected to fail because we know
    the set iteration order causes flaky behavior.
    """
    ids = {"5", "3", "1", "4", "2"}
    summary = generate_summary(ids)
    assert summary == "Unique IDs: 1, 2, 3, 4, 5"
