"""Data deduplication logic with FIXED deterministic behavior."""

import csv
from typing import List, Dict, Tuple


def deduplicate_records(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Remove duplicate records based on 'id' field.
    
    FIXED: Returns a sorted list of unique IDs instead of a set,
    ensuring deterministic iteration order.
    
    Args:
        records: List of record dictionaries
    
    Returns:
        Tuple of (unique_records, unique_ids_list)
        - unique_records: List of deduplicated records (order preserved from input)
        - unique_ids_list: Sorted list of unique IDs (deterministic order)
    
    Example:
        >>> records = [
        ...     {"id": "1", "name": "Alice"},
        ...     {"id": "2", "name": "Bob"},
        ...     {"id": "1", "name": "Alice"}  # duplicate
        ... ]
        >>> unique, ids = deduplicate_records(records)
        >>> len(unique)
        2
        >>> ids
        ['1', '2']  # Always in sorted order
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


def process_csv(file_path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Read CSV file and deduplicate records.
    
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
