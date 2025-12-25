"""Fixed report generation: deterministic summaries and report IDs."""

from typing import List, Dict, Iterable
import hashlib


def _normalize_ids(ids: Iterable[str]) -> List[str]:
    """Return a sorted list of IDs (works if input is set/list/tuple)."""
    return sorted(ids)


def generate_summary(unique_ids) -> str:
    """
    Generate a deterministic summary string from unique IDs.

    Accepts either a set or a list of IDs; output is always sorted
    so it's deterministic across processes.
    """
    ids_sorted = _normalize_ids(unique_ids)
    ids_str = ", ".join(str(i) for i in ids_sorted)
    return f"Unique IDs: {ids_str}"


def create_report(records: List[Dict[str, str]], unique_ids) -> Dict[str, any]:
    """
    Create a deterministic report. The summary (and therefore the
    report hash/ID) is stable because IDs are normalized and sorted.
    """
    summary = generate_summary(unique_ids)
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]

    report = {
        "total_unique": len(list(unique_ids)),
        "summary": summary,
        "report_id": f"RPT-{report_hash}",
        "records": records,
    }
    return report


# Backwards-compatible helpers

def generate_summary_fixed(unique_ids_list: List[str]) -> str:
    return generate_summary(unique_ids_list)


def create_report_fixed(records: List[Dict[str, str]], unique_ids_list: List[str]) -> Dict[str, any]:
    return create_report(records, unique_ids_list)
