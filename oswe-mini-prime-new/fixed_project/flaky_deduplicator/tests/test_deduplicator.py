"""Deterministic tests for deduplication and reporting."""

from deduplicator import deduplicate_records, generate_summary, create_report


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

    # Deterministic sorted order
    assert unique_ids == ["1", "2", "3"]


def test_summary_generation_is_deterministic():
    records = [
        {"id": "3", "name": "C"},
        {"id": "1", "name": "A"},
        {"id": "2", "name": "B"},
    ]

    _, unique_ids = deduplicate_records(records)

    summary = generate_summary(unique_ids)
    assert summary == "Unique IDs: 1, 2, 3"

    # Re-running should be identical
    for _ in range(5):
        _, uids = deduplicate_records(records)
        assert generate_summary(uids) == summary


def test_report_id_consistency():
    records = [
        {"id": "100", "name": "Test1"},
        {"id": "200", "name": "Test2"},
        {"id": "300", "name": "Test3"},
    ]

    unique_records, unique_ids = deduplicate_records(records)

    r1 = create_report(unique_records, unique_ids)
    r2 = create_report(unique_records, unique_ids)

    assert r1["report_id"] == r2["report_id"]


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


def test_repeated_runs_produce_identical_reports():
    records = [
        {"id": "Z9", "name": "Zoe"},
        {"id": "A1", "name": "Alice"},
        {"id": "M5", "name": "Mike"},
        {"id": "A1", "name": "Alice"},  # dup
    ]

    first = None
    for _ in range(10):
        unique_records, unique_ids = deduplicate_records(records)
        report = create_report(unique_records, unique_ids)
        if first is None:
            first = report
        else:
            assert report == first
