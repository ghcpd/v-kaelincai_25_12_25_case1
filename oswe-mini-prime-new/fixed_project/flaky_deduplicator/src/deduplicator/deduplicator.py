"""Deterministic data deduplication.

This module ensures determinism by returning a sorted list of unique IDs
(rather than a set) so callers can produce deterministic strings and hashes.
"""

import csv
from typing import List, Dict, Tuple


def deduplicate_records(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Remove duplicate records based on 'id' field and return a deterministic
    sorted list of unique IDs.

    Args:
        records: List of record dictionaries

    Returns:
        Tuple of (unique_records, unique_ids_list)
        - unique_records: List of deduplicated records (order preserved from input)
        - unique_ids_list: SORTED list of unique IDs (deterministic order)
    """
    seen_ids = set()
    unique_records = []

    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)

    # Convert set to sorted list for deterministic output
    unique_ids_list = sorted(seen_ids)

    return unique_records, unique_ids_list


def process_csv(file_path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Read CSV file and deduplicate records. Returns deterministic unique id list.

    Args:
        file_path: Path to CSV file

    Returns:
        Tuple of (unique_records, unique_ids_list)
    """
    records = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return deduplicate_records(records)
