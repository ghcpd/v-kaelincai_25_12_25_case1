#!/usr/bin/env python3
"""Lightweight runtime validator to exercise deduplication and report generation.

This script is intended to be run from the project root and will print
summary and report id for the sample CSV. Run it under different
PYTHONHASHSEED values to verify deterministic behavior across processes.
"""
import os
import sys

project_dir = os.path.dirname(__file__)
# Ensure the src/ directory is on sys.path for local imports
sys.path.insert(0, os.path.join(project_dir, "src"))

from deduplicator import process_csv, create_report


def run_once():
    csv_path = os.path.join(project_dir, "data", "sample_data.csv")
    records, unique_ids = process_csv(csv_path)
    report = create_report(records, unique_ids)
    print("Summary:", report["summary"])
    print("Report ID:", report["report_id"])
    print("Total unique:", report["total_unique"])
    print("Unique IDs:", unique_ids)


if __name__ == "__main__":
    run_once()
