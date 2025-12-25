"""Deterministic report generation (fixed).

Functions accept either a set or a list of IDs but always produce
deterministic output by sorting IDs before creating strings or hashes.
"""
from typing import Iterable, List, Dict, Any
import hashlib


def _normalize_ids(ids: Iterable[str]) -> List[str]:
    """Return a deterministic, sorted list of id strings."""
    return sorted((str(i) for i in ids), key=str)


def generate_summary(unique_ids: Iterable[str]) -> str:
    """Generate a deterministic summary string from unique IDs.

    Works with sets or lists; output is always sorted by string value.
    """
    ids_list = _normalize_ids(unique_ids)
    ids_str = ", ".join(ids_list)
    return f"Unique IDs: {ids_str}"


def create_report(records: List[Dict[str, str]], unique_ids: Iterable[str]) -> Dict[str, Any]:
    """Create a deterministic deduplication report.

    The summary is deterministic (sorted IDs) so the derived hash and
    `report_id` are stable across processes and runs.
    """
    ids_list = _normalize_ids(unique_ids)
    summary = generate_summary(ids_list)
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]

    return {
        "total_unique": len(ids_list),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",
        "records": records,
    }


# Backwards-compatible fixed helpers (kept for clarity)
def generate_summary_fixed(unique_ids: List[str]) -> str:
    return generate_summary(unique_ids)


def create_report_fixed(records: List[Dict[str, str]], unique_ids: List[str]) -> Dict[str, Any]:
    return create_report(records, unique_ids)
