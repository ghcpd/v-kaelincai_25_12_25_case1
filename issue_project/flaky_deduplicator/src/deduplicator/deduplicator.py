"""Data deduplication logic with flaky behavior due to set ordering."""

import csv
from typing import List, Dict, Tuple


def deduplicate_records(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], set]:
    """
    Remove duplicate records based on 'id' field.
    
    BUG: Returns a set of unique IDs, which has non-deterministic iteration order.
    This causes issues when the set is used to generate output strings or reports.
    
    Args:
        records: List of record dictionaries
    
    Returns:
        Tuple of (unique_records, unique_ids_set)
        - unique_records: List of deduplicated records (order preserved from input)
        - unique_ids_set: Set of unique IDs (PROBLEMATIC: iteration order undefined!)
    
    Example:
        >>> records = [
        ...     {"id": "1", "name": "Alice"},
        ...     {"id": "2", "name": "Bob"},
        ...     {"id": "1", "name": "Alice"}  # duplicate
        ... ]
        >>> unique, ids = deduplicate_records(records)
        >>> len(unique)
        2
        >>> ids  # Order may vary: {1, 2} or {2, 1} depending on Python hash seed
    """
    seen_ids = set()
    unique_records = []
    
    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)
    
    # BUG: Returning the set directly
    # The caller might iterate over this set to generate strings,
    # leading to non-deterministic output order
    return unique_records, seen_ids


def process_csv(file_path: str) -> Tuple[List[Dict[str, str]], set]:
    """
    Read CSV file and deduplicate records.
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        Tuple of (unique_records, unique_ids_set)
    """
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    return deduplicate_records(records)


def deduplicate_records_fixed(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    FIXED version: Returns a sorted list instead of a set.
    
    Args:
        records: List of record dictionaries
    
    Returns:
        Tuple of (unique_records, unique_ids_list)
        - unique_records: List of deduplicated records
        - unique_ids_list: SORTED list of unique IDs (deterministic order)
    """
    seen_ids = set()
    unique_records = []
    
    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)
    
    # FIX: Convert set to sorted list for deterministic output
    unique_ids_list = sorted(seen_ids)
    
    return unique_records, unique_ids_list
