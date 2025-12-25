import pytest
from src.deduplicator.deduplicator import deduplicate_records, load_records_from_csv
from src.deduplicator.reporter import generate_summary, create_report

def test_deduplicate_records():
    records = [
        {'id': '1', 'name': 'Alice'},
        {'id': '2', 'name': 'Bob'},
        {'id': '1', 'name': 'Alice'},
        {'id': '3', 'name': 'Charlie'}
    ]
    unique_ids = deduplicate_records(records)
    assert unique_ids == ['1', '2', '3']  # Sorted as strings

def test_generate_summary():
    unique_ids = ['1', '2', '3']
    summary = generate_summary(unique_ids)
    assert summary == "Unique IDs: 1, 2, 3"

def test_create_report():
    summary = "Unique IDs: 1, 2, 3"
    report = create_report(summary)
    assert report['summary'] == summary
    assert report['report_id'].startswith('RPT-')
    # Since hash is deterministic, report_id should be fixed
    # For "Unique IDs: 1, 2, 3", md5[:8] is 'something', but we'll check in full pipeline

def test_full_pipeline():
    # Load from CSV
    records = load_records_from_csv('data/sample_data.csv')
    unique_ids = deduplicate_records(records)
    summary = generate_summary(unique_ids)
    report = create_report(summary)
    # Assert deterministic values
    assert unique_ids == ['1', '2', '3', '4']
    assert summary == "Unique IDs: 1, 2, 3, 4"
    # Expected report_id for "Unique IDs: 1, 2, 3, 4"
    assert report['report_id'] == 'RPT-50748ef2'