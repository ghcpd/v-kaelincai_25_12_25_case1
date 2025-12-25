"""Data deduplication module with intentional flaky behavior."""

from .deduplicator import deduplicate_records, process_csv
from .reporter import generate_summary, create_report

__all__ = ['deduplicate_records', 'process_csv', 'generate_summary', 'create_report']
