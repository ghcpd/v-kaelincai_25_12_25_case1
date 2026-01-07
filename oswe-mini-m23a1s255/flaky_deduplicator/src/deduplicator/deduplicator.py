"""Deterministic data deduplication (fixed).

This module preserves the original public API but ensures deterministic
ordering for any output that may be relied upon by callers or tests.

Key fix:
- deduplicate_records() now returns a SORTED list of unique IDs (not a set).
  This guarantees the same output every run and across processes.

Compatibility:
- Function name and high-level behavior are preserved (returns
  (unique_records, unique_ids)). The type of `unique_ids` is a list
  (deterministic) instead of a set (non-deterministic iteration order).
"""

import csv
from typing import List, Dict, Tuple, Iterable


def deduplicate_records(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """Remove duplicate records and return deterministic list of unique ids.

    Behavior changes (intentional and compatible):
    - `unique_records` preserves the first-seen order from the input
    - `unique_ids` is a SORTED list of unique id strings (deterministic)

    Returning a list for `unique_ids` keeps membership/len checks working
    while eliminating nondeterministic iteration order from sets.
    """
    seen_ids = set()
    unique_records = []

    for record in records:
        record_id = record.get("id", "")
        if record_id and record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)

    # FIX: return a deterministic, sorted list of IDs instead of a set
    unique_ids_list = sorted(seen_ids, key=str)
    return unique_records, unique_ids_list


def process_csv(file_path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """Read CSV file and deduplicate records (deterministic)."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return deduplicate_records(records)


def deduplicate_records_fixed(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """Backward-compatible reference implementation (returns sorted list).

    Kept for clarity / backwards reference in tests and documentation.
    """
    return deduplicate_records(records)
