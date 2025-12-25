"""Fixed data deduplication: deterministic outputs (no set iteration used)."""

import csv
from typing import List, Dict, Tuple, Iterable


def deduplicate_records(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Deterministic deduplication.

    - Preserves input order for `unique_records`.
    - Returns a **sorted list** of unique IDs (deterministic) instead of a set.

    Returns:
        (unique_records, unique_ids_list)
    """
    seen_ids = set()
    unique_records = []

    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)

    # Return a sorted list to guarantee deterministic order across processes
    unique_ids_list = sorted(seen_ids)
    return unique_records, unique_ids_list


def process_csv(file_path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return deduplicate_records(records)


# Keep a "_fixed" helper for clarity / backwards-compatibility of tests
def deduplicate_records_fixed(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    return deduplicate_records(records)
