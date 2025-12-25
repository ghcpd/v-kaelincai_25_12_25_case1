# Data Deduplicator - Flaky Behavior Demo

## Overview

This project demonstrates a **flaky behavior bug** in a data deduplication tool. The bug causes the same input data to produce different output strings and report IDs on different runs, making tests unreliable.

## The Problem: Flaky Behavior

**Symptom**: Running the same deduplication process multiple times with identical input produces different summary strings and report IDs.

```python
from deduplicator import deduplicate_records, generate_summary, create_report

records = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "1", "name": "Alice"},  # duplicate
    {"id": "3", "name": "Carol"},
]

unique_records, unique_ids = deduplicate_records(records)

# First run
summary1 = generate_summary(unique_ids)
# "Unique IDs: 1, 2, 3"

# Second run (new Python process)
summary2 = generate_summary(unique_ids)
# "Unique IDs: 2, 3, 1"  # Different order!

# Third run
summary3 = generate_summary(unique_ids)
# "Unique IDs: 3, 1, 2"  # Different again!
```

## Root Cause

The bug is in how the code handles set iteration:

**Problem 1: Returning a set from deduplication**

```python
# In deduplicator.py
def deduplicate_records(records):
    seen_ids = set()
    unique_records = []
    
    for record in records:
        if record["id"] not in seen_ids:
            seen_ids.add(record["id"])
            unique_records.append(record)
    
    # BUG: Returning a set with undefined iteration order
    return unique_records, seen_ids
```

**Problem 2: Iterating over the set to generate strings**

```python
# In reporter.py
def generate_summary(unique_ids):
    # BUG: Iterating over set - order is undefined!
    ids_str = ", ".join(str(id) for id in unique_ids)
    summary = f"Unique IDs: {ids_str}"
    return summary
```

### Why This Causes Flaky Behavior

1. **Python's Hash Randomization**: Since Python 3.3, dictionary and set iteration order depends on `PYTHONHASHSEED`
2. **Process-Specific**: Each Python process can have a different hash seed
3. **Non-Deterministic Output**: Same set → different iteration orders → different string outputs
4. **Cascading Effects**: Summary string affects report hash → report ID changes too

## Project Structure

```
flaky_deduplicator/
├── README.md                    # This file
├── KNOWN_ISSUE.md              # Detailed bug analysis
├── requirements.txt            # Dependencies (pytest only)
├── pytest.ini                  # Pytest configuration
├── data/
│   └── sample_data.csv        # Sample CSV with duplicates
├── src/
│   └── deduplicator/
│       ├── __init__.py
│       ├── deduplicator.py    # Core deduplication logic (buggy)
│       └── reporter.py        # Report generation (buggy)
└── tests/
    └── test_deduplicator.py   # Flaky tests demonstrating the bug
```

## Setup and Installation

### Requirements
- Python 3.12+
- pytest

### Install

```powershell
# Navigate to project directory
cd flaky_deduplicator

# Create virtual environment (optional)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

### Observe the Flaky Behavior

```powershell
# Run tests
pytest tests/ -v

# Run a specific flaky test multiple times
pytest tests/test_deduplicator.py::test_summary_generation -v

# Run in different processes to see different results
python -c "import subprocess; [subprocess.run(['pytest', 'tests/test_deduplicator.py::test_summary_generation', '-v']) for _ in range(5)]"
```

### Expected Test Results

- `test_basic_deduplication` - ✅ Usually passes (doesn't check string order)
- `test_summary_generation` - ❌ **FLAKY** (checks exact string match)
- `test_summary_consistency` - ❌ **FLAKY** (may pass in same process, fails across processes)
- `test_report_id_consistency` - ❌ **FLAKY** (report ID depends on summary)
- `test_full_deduplication_pipeline` - ❌ **FLAKY** (end-to-end test)
- `test_fixed_version_is_deterministic` - ✅ Always passes (uses sorted lists)
- `test_fixed_report_consistency` - ✅ Always passes (fixed version)

## Demonstrating the Bug

### Python REPL Demo

```python
from deduplicator import generate_summary

# Create the same set multiple times
ids = {"5", "3", "1", "4", "2"}

# Run multiple times - you'll see different orders
for i in range(5):
    summary = generate_summary(ids)
    print(f"Run {i+1}: {summary}")

# Possible outputs (order varies):
# Run 1: Unique IDs: 1, 2, 3, 4, 5
# Run 2: Unique IDs: 3, 1, 4, 2, 5
# Run 3: Unique IDs: 2, 5, 1, 3, 4
# Run 4: Unique IDs: 4, 2, 5, 1, 3
# Run 5: Unique IDs: 1, 3, 2, 5, 4
```

### Process-Level Demonstration

```powershell
# Run the same test in different processes
for ($i=1; $i -le 5; $i++) {
    Write-Host "Process $i:"
    python -c "from deduplicator import generate_summary; print(generate_summary({'10', '20', '30'}))"
}
```

## The Fix

The solution: **Convert sets to sorted lists before generating output**

### Fixed Deduplicator

```python
def deduplicate_records_fixed(records):
    seen_ids = set()
    unique_records = []
    
    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record["id"])
            unique_records.append(record)
    
    # FIX: Convert to sorted list
    unique_ids_list = sorted(seen_ids)
    
    return unique_records, unique_ids_list
```

### Fixed Reporter

```python
def generate_summary_fixed(unique_ids_list):
    # unique_ids_list is already sorted
    ids_str = ", ".join(str(id) for id in unique_ids_list)
    summary = f"Unique IDs: {ids_str}"
    return summary
```

Fixed versions are available in the same modules as `*_fixed()` functions.

## Key Lessons

1. **Set iteration order is undefined**: Never rely on set iteration order for output generation
2. **Hash randomization is a security feature**: `PYTHONHASHSEED` varies across processes by design
3. **Sort before outputting**: Always convert sets to sorted lists when order matters
4. **Test across processes**: Flaky behavior often only appears when tests run in separate processes
5. **Same process ≠ deterministic**: Even within one process, set order can surprise you

## Common Mistakes

### ❌ Wrong: Relying on set order

```python
ids = {1, 2, 3}
print(", ".join(str(x) for x in ids))  # Order undefined!
```

### ✅ Right: Sort before using

```python
ids = {1, 2, 3}
print(", ".join(str(x) for x in sorted(ids)))  # Order guaranteed
```

### ❌ Wrong: Testing in same process only

```python
# This might pass even with the bug
def test():
    result1 = generate_summary(ids)
    result2 = generate_summary(ids)
    assert result1 == result2  # May pass in same process!
```

### ✅ Right: Test determinism explicitly

```python
def test():
    # Use sorted lists
    ids_list = sorted(ids)
    result = generate_summary_fixed(ids_list)
    assert result == "Unique IDs: 1, 2, 3"  # Always passes
```

## When Does This Bug Appear?

- ✅ Running tests in separate Python processes
- ✅ CI/CD pipelines (each test run is a new process)
- ✅ Using `pytest-xdist` for parallel testing
- ✅ Different machines or environments
- ❌ Sometimes masked when running all tests in same process

## Related Issues

This pattern occurs whenever:
- Generating strings from sets
- Creating hashes from set-based data
- Serializing sets to JSON/XML
- Logging or displaying set contents
- Comparing string representations of sets

## References

- [PEP 456: Secure and interchangeable hash algorithm](https://www.python.org/dev/peps/pep-0456/)
- [Python Documentation: Set types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [PYTHONHASHSEED environment variable](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED)

---

**This is an educational project demonstrating flaky behavior in data processing code.**
