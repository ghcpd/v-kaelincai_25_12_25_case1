"""Report generation with flaky behavior due to set iteration."""

from typing import List, Dict, Set
import hashlib


def generate_summary(unique_ids: Set[str]) -> str:
    """
    Generate a summary string from unique IDs.
    
    BUG: Iterates over a set to create a string, causing non-deterministic output!
    
    The iteration order of a set depends on:
    - Python's hash randomization (PYTHONHASHSEED)
    - Memory addresses
    - Python version
    
    This means the same set will produce different strings across different runs.
    
    Args:
        unique_ids: Set of unique record IDs
    
    Returns:
        Summary string with unique IDs
    
    Example (FLAKY):
        >>> ids = {"3", "1", "2"}
        >>> generate_summary(ids)
        'Unique IDs: 1, 2, 3'  # First run
        
        # Run in a new Python process:
        >>> generate_summary(ids)
        'Unique IDs: 2, 3, 1'  # Different order!
    """
    # BUG: Directly iterating over set - order is undefined!
    ids_str = ", ".join(str(id) for id in unique_ids)
    
    summary = f"Unique IDs: {ids_str}"
    return summary


def create_report(records: List[Dict[str, str]], unique_ids: Set[str]) -> Dict[str, any]:
    """
    Create a deduplication report.
    
    BUG: Includes summary that depends on set iteration order.
    Also generates a hash based on the summary, which will be different each time!
    
    Args:
        records: List of unique records
        unique_ids: Set of unique IDs (PROBLEMATIC!)
    
    Returns:
        Report dictionary with summary, count, and hash
    """
    summary = generate_summary(unique_ids)
    
    # BUG: Hash depends on summary, which depends on set iteration order
    # Different runs will produce different hashes for the same data!
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]
    
    report = {
        "total_unique": len(unique_ids),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",  # FLAKY: changes across runs
        "records": records
    }
    
    return report


def generate_summary_fixed(unique_ids: List[str]) -> str:
    """
    FIXED version: Takes a sorted list instead of a set.
    
    Args:
        unique_ids: Sorted list of unique record IDs
    
    Returns:
        Deterministic summary string
    """
    # FIX: unique_ids is already sorted, so output is deterministic
    ids_str = ", ".join(str(id) for id in unique_ids)
    summary = f"Unique IDs: {ids_str}"
    return summary


def create_report_fixed(records: List[Dict[str, str]], unique_ids: List[str]) -> Dict[str, any]:
    """
    FIXED version: Takes a sorted list instead of a set.
    
    Args:
        records: List of unique records
        unique_ids: Sorted list of unique IDs (deterministic)
    
    Returns:
        Deterministic report dictionary
    """
    summary = generate_summary_fixed(unique_ids)
    
    # Now hash is deterministic because summary is deterministic
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]
    
    report = {
        "total_unique": len(unique_ids),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",
        "records": records
    }
    
    return report
