"""Deterministic deduplicator package (fixed public API).

This package exposes the same top-level names as the original project
but the implementations are deterministic so tests and outputs are
stable across runs and processes.
"""

from .deduplicator import deduplicate_records, process_csv, deduplicate_records_fixed
from .reporter import generate_summary, create_report, generate_summary_fixed, create_report_fixed

__all__ = [
    "deduplicate_records",
    "process_csv",
    "generate_summary",
    "create_report",
    "deduplicate_records_fixed",
    "generate_summary_fixed",
    "create_report_fixed",
]
