"""Report generation with FIXED deterministic behavior."""

from typing import List, Dict
import hashlib


def generate_summary(unique_ids: List[str]) -> str:
    """
    Generate a summary string from unique IDs.
    
    FIXED: Takes a sorted list instead of a set, ensuring deterministic output.
    
    Args:
        unique_ids: Sorted list of unique record IDs
    
    Returns:
        Deterministic summary string with unique IDs
    
    Example:
        >>> ids = ['1', '2', '3']
        >>> generate_summary(ids)
        'Unique IDs: 1, 2, 3'  # Always the same
    """
    # FIX: unique_ids is already sorted, so output is deterministic
    ids_str = ", ".join(str(id) for id in unique_ids)
    summary = f"Unique IDs: {ids_str}"
    return summary


def create_report(records: List[Dict[str, str]], unique_ids: List[str]) -> Dict[str, any]:
    """
    Create a deduplication report.
    
    FIXED: Takes a sorted list instead of a set, ensuring deterministic report IDs.
    
    Args:
        records: List of unique records
        unique_ids: Sorted list of unique IDs (deterministic)
    
    Returns:
        Deterministic report dictionary with summary, count, and hash
    """
    summary = generate_summary(unique_ids)
    
    # FIX: Hash is now deterministic because summary is deterministic
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]
    
    report = {
        "total_unique": len(unique_ids),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",
        "records": records
    }
    
    return report
