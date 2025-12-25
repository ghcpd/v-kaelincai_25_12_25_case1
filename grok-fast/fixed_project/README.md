# Fixed Data Deduplicator

This project is a fixed version of the Data Deduplicator tool. The original version suffered from flaky behavior due to non-deterministic output caused by iterating over Python sets in undefined order.

## Fix Applied

The core issue was in the `deduplicate_records()` function, which returned a set of unique IDs. Since sets have no guaranteed order, iterating over them in `generate_summary()` and `create_report()` led to different summary strings and report IDs across runs.

### Changes Made

1. **deduplicator.py**: Modified `deduplicate_records()` to return a sorted list of unique IDs instead of a set.
2. **reporter.py**: Functions now work with sorted lists, ensuring deterministic output.
3. **tests**: Updated tests to expect deterministic results and removed any flaky test markers.

## Deterministic Output

- Same input data always produces the same unique IDs in sorted order.
- Summary strings are consistent.
- Report IDs are generated deterministically from the summary.

## Running the Project

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`
3. Tests should pass reliably on every run.