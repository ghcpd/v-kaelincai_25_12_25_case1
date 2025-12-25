"""Deterministic report generation utilities."""

from typing import List, Dict, Any
import hashlib


def generate_summary(unique_ids: List[str]) -> str:
    """
    Generate a deterministic summary string from a sorted list of unique IDs.

    Args:
        unique_ids: Sorted list of unique record IDs

    Returns:
        Summary string with unique IDs
    """
    ids_str = ", ".join(str(id) for id in unique_ids)
    summary = f"Unique IDs: {ids_str}"
    return summary


def create_report(records: List[Dict[str, str]], unique_ids: List[str]) -> Dict[str, Any]:
    """
    Create a deterministic deduplication report built from sorted unique IDs.

    Args:
        records: List of unique records
        unique_ids: Sorted list of unique IDs (deterministic)

    Returns:
        Deterministic report dictionary
    """
    summary = generate_summary(unique_ids)

    # Deterministic hash computed from deterministic summary
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]

    report = {
        "total_unique": len(unique_ids),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",
        "records": records,
    }

    return report
