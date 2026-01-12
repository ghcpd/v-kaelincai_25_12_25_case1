"""Tests for deduplication — deterministic, flaky issues fixed."""

import pytest
from deduplicator import deduplicate_records, generate_summary, create_report
from deduplicator.deduplicator import deduplicate_records_fixed
from deduplicator.reporter import generate_summary_fixed, create_report_fixed


def test_basic_deduplication():
    records = [
        {"id": "1", "name": "Alice", "city": "NYC"},
        {"id": "2", "name": "Bob", "city": "LA"},
        {"id": "1", "name": "Alice", "city": "NYC"},  # duplicate
        {"id": "3", "name": "Carol", "city": "SF"},
    ]
    unique_records, unique_ids = deduplicate_records(records)
    assert len(unique_records) == 3
    assert len(unique_ids) == 3
    assert unique_ids == ["1", "2", "3"]


def test_summary_generation():
    unique_ids = {"3", "1", "2"}
    summary = generate_summary(unique_ids)
    assert summary == "Unique IDs: 1, 2, 3"


def test_summary_consistency():
    ids1 = {"10", "20", "30"}
    ids2 = {"10", "20", "30"}
    ids3 = {"10", "20", "30"}
    summary1 = generate_summary(ids1)
    summary2 = generate_summary(ids2)
    summary3 = generate_summary(ids3)
    assert summary1 == summary2 == summary3


def test_report_id_consistency():
    records = [
        {"id": "100", "name": "Test1"},
        {"id": "200", "name": "Test2"},
        {"id": "300", "name": "Test3"},
    ]
    unique_ids = {"100", "200", "300"}
    report1 = create_report(records, unique_ids)
    report2 = create_report(records, unique_ids)
    assert report1["report_id"] == report2["report_id"]


def test_full_deduplication_pipeline():
    records = [
        {"id": "A1", "name": "Alice", "dept": "Engineering"},
        {"id": "B2", "name": "Bob", "dept": "Sales"},
        {"id": "A1", "name": "Alice", "dept": "Engineering"},  # dup
        {"id": "C3", "name": "Carol", "dept": "Marketing"},
        {"id": "B2", "name": "Bob", "dept": "Sales"},  # dup
    ]
    unique_records, unique_ids = deduplicate_records(records)
    report = create_report(unique_records, unique_ids)
    assert report["total_unique"] == 3
    assert len(report["records"]) == 3
    assert report["summary"] == "Unique IDs: A1, B2, C3"


def test_fixed_version_is_deterministic():
    records = [
        {"id": "Z9", "name": "Zoe"},
        {"id": "A1", "name": "Alice"},
        {"id": "M5", "name": "Mike"},
        {"id": "A1", "name": "Alice"},  # dup
    ]
    results = []
    for _ in range(10):
        unique_records, unique_ids_list = deduplicate_records_fixed(records)
        summary = generate_summary_fixed(unique_ids_list)
        results.append(summary)
    assert all(r == results[0] for r in results)
    assert results[0] == "Unique IDs: A1, M5, Z9"


def test_fixed_report_consistency():
    records = [
        {"id": "30", "name": "Test"},
        {"id": "10", "name": "Test"},
        {"id": "20", "name": "Test"},
    ]
    unique_records, unique_ids_list = deduplicate_records_fixed(records)
    reports = [create_report_fixed(unique_records, unique_ids_list) for _ in range(5)]
    assert all(r["report_id"] == reports[0]["report_id"] for r in reports)
    assert all(r["summary"] == reports[0]["summary"] for r in reports)


def test_known_flaky_summary():
    ids = {"5", "3", "1", "4", "2"}
    summary = generate_summary(ids)
    assert summary == "Unique IDs: 1, 2, 3, 4, 5"