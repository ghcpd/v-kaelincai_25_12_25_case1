# Known Issue: Non-Deterministic Set Iteration

**Type:** Flaky Behavior / Non-Deterministic Output

**Category:** Bug-related → Flaky behavior

**Classification:** Same input gives inconsistent outputs

## Symptom

The deduplication tool generates different summary strings and report IDs when processing the same input data across different runs or processes.

### Example

```python
records = [
    {"id": "10", "name": "Alice"},
    {"id": "20", "name": "Bob"},
    {"id": "10", "name": "Alice"},  # duplicate
    {"id": "30", "name": "Carol"}
]

unique_records, unique_ids = deduplicate_records(records)
summary = generate_summary(unique_ids)

# Run 1: "Unique IDs: 10, 20, 30"
# Run 2: "Unique IDs: 20, 30, 10"
# Run 3: "Unique IDs: 30, 10, 20"
```

### Variability Observed

- **Summary strings**: Order of IDs varies (e.g., "10, 20, 30" vs "20, 30, 10")
- **Report IDs**: Hash-based IDs change (e.g., "RPT-a3c5f2e1" vs "RPT-f1e2c5a3")
- **Frequency**: Appears consistently across different Python processes
- **Within-process**: May appear consistent within a single process

## Root Cause

### Primary Issue: Set Iteration Order Dependency

The code returns and iterates over Python sets, whose iteration order is undefined and varies across different Python processes due to hash randomization.

**Problem Location 1: `deduplicator.py`**

```python
def deduplicate_records(records):
    seen_ids = set()
    unique_records = []
    
    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)
    
    # BUG: Returning a set with undefined iteration order
    return unique_records, seen_ids
```

**Problem Location 2: `reporter.py`**

```python
def generate_summary(unique_ids):
    # BUG: Iterating over set - order is undefined!
    ids_str = ", ".join(str(id) for id in unique_ids)
    summary = f"Unique IDs: {ids_str}"
    return summary

def create_report(records, unique_ids):
    summary = generate_summary(unique_ids)
    
    # BUG: Hash depends on summary, which depends on set order
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]
    report_id = f"RPT-{report_hash}"  # Different across runs!
    
    return {"report_id": report_id, "summary": summary, ...}
```

### Why Set Iteration Order Is Undefined

1. **Hash Randomization (PYTHONHASHSEED)**:
   - Introduced in Python 3.3 for security
   - Randomizes hash values for strings and bytes
   - Different processes get different hash seeds
   - Set iteration order depends on hash values

2. **Memory Layout**:
   - Set implementation uses hash tables
   - Iteration follows internal bucket order
   - Order depends on insertion history and hash collisions

3. **No Guarantees**:
   - Python documentation explicitly states set iteration order is undefined
   - Even if it appears consistent in testing, it's not guaranteed

### Cascading Effects

```
Set iteration order varies
    ↓
Summary string varies ("10, 20, 30" vs "20, 30, 10")
    ↓
MD5 hash varies
    ↓
Report ID varies ("RPT-a3c5f2e1" vs "RPT-f1e2c5a3")
    ↓
Test assertions fail
```

## Impact

### On Tests

- **Flaky tests**: `test_summary_generation()` fails ~60-70% of the time in CI
- **False positives**: Tests pass locally, fail in CI (different processes)
- **CI/CD instability**: Pipeline results unpredictable
- **Debug confusion**: "It worked on my machine"

### On Production

- **Inconsistent reports**: Same data generates different report IDs
- **Tracking problems**: Cannot correlate reports across runs
- **User confusion**: "Why did my report ID change?"
- **Cache misses**: Report IDs used as cache keys fail to match

### On Development

- **Hard to reproduce**: Issue appears/disappears unpredictably
- **Misleading**: Works in development, fails in production
- **Time waste**: Developers chase phantom bugs

## Reproduction Steps

### Method 1: Multiple Process Runs

```powershell
# Run the same test in separate processes
for ($i=1; $i -le 10; $i++) {
    Write-Host "Run $i:"
    python -m pytest tests/test_deduplicator.py::test_summary_generation -v
}

# Observe: Some passes, some failures
```

### Method 2: Direct Python Execution

```python
# test_flaky.py
from deduplicator import deduplicate_records, generate_summary

records = [
    {"id": "100", "name": "Test1"},
    {"id": "200", "name": "Test2"},
    {"id": "300", "name": "Test3"}
]

unique_records, unique_ids = deduplicate_records(records)
summary = generate_summary(unique_ids)
print(summary)
```

```powershell
# Run in different processes
for ($i=1; $i -le 5; $i++) {
    python test_flaky.py
}

# Output varies:
# Run 1: Unique IDs: 100, 200, 300
# Run 2: Unique IDs: 200, 300, 100
# Run 3: Unique IDs: 300, 100, 200
# ...
```

### Method 3: Explicit Hash Seed Control

```powershell
# Force different hash seeds
$env:PYTHONHASHSEED=0; python -c "from deduplicator import generate_summary; print(generate_summary({'A', 'B', 'C'}))"
$env:PYTHONHASHSEED=1; python -c "from deduplicator import generate_summary; print(generate_summary({'A', 'B', 'C'}))"
$env:PYTHONHASHSEED=2; python -c "from deduplicator import generate_summary; print(generate_summary({'A', 'B', 'C'}))"

# Different outputs expected
```

## Fix

### Solution: Convert Sets to Sorted Lists

**Step 1: Fix `deduplicate_records()`**

```python
def deduplicate_records_fixed(records):
    seen_ids = set()
    unique_records = []
    
    for record in records:
        record_id = record.get("id", "")
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            unique_records.append(record)
    
    # FIX: Convert set to sorted list before returning
    unique_ids_list = sorted(seen_ids)
    
    return unique_records, unique_ids_list
```

**Step 2: Fix `generate_summary()`**

```python
def generate_summary_fixed(unique_ids_list):
    # unique_ids_list is already sorted, so order is deterministic
    ids_str = ", ".join(str(id) for id in unique_ids_list)
    summary = f"Unique IDs: {ids_str}"
    return summary
```

**Step 3: Fix `create_report()`**

```python
def create_report_fixed(records, unique_ids_list):
    summary = generate_summary_fixed(unique_ids_list)
    
    # Now hash is deterministic because summary is deterministic
    report_hash = hashlib.md5(summary.encode()).hexdigest()[:8]
    
    return {
        "report_id": f"RPT-{report_hash}",
        "summary": summary,
        "total_unique": len(unique_ids_list),
        "records": records
    }
```

### Why This Works

1. **`sorted()` is deterministic**: Always returns elements in the same order
2. **String comparison works**: "10, 20, 30" always equals "10, 20, 30"
3. **Hash is stable**: MD5 of same string always produces same hash
4. **No process dependency**: Works the same across all Python processes

## Verification

After applying the fix:

```python
from deduplicator.deduplicator import deduplicate_records_fixed
from deduplicator.reporter import generate_summary_fixed, create_report_fixed

records = [{"id": "Z"}, {"id": "A"}, {"id": "M"}]

# Run 10 times
results = []
for _ in range(10):
    unique_records, unique_ids_list = deduplicate_records_fixed(records)
    summary = generate_summary_fixed(unique_ids_list)
    results.append(summary)

# All should be identical
assert all(r == results[0] for r in results)
assert results[0] == "Unique IDs: A, M, Z"  # Sorted!
```

## Prevention: Best Practices

### 1. Never Rely on Set/Dict Order for Output

```python
# ❌ WRONG
def format_ids(ids_set):
    return ", ".join(ids_set)  # Order undefined!

# ✅ RIGHT
def format_ids(ids_set):
    return ", ".join(sorted(ids_set))  # Order guaranteed
```

### 2. Sort Before Serializing

```python
# ❌ WRONG
import json
data = {"ids": list(id_set)}  # List order from set is undefined
json.dumps(data)

# ✅ RIGHT
import json
data = {"ids": sorted(id_set)}  # Sorted order
json.dumps(data)
```

### 3. Use Deterministic Data Structures

```python
# ❌ RISKY: Set
unique_items = set(items)
for item in unique_items:  # Order undefined
    process(item)

# ✅ SAFE: Sorted list
unique_items = sorted(set(items))
for item in unique_items:  # Order defined
    process(item)
```

### 4. Test Across Processes

```python
# ❌ INSUFFICIENT: Same process test
def test_same_process():
    result1 = function()
    result2 = function()
    assert result1 == result2  # May pass even with bug

# ✅ SUFFICIENT: Subprocess test
import subprocess
def test_cross_process():
    result1 = subprocess.check_output(["python", "-c", "import module; print(module.function())"])
    result2 = subprocess.check_output(["python", "-c", "import module; print(module.function())"])
    assert result1 == result2
```

### 5. Document Ordering Requirements

```python
def generate_report(unique_ids: List[str]) -> str:
    """
    Generate report from unique IDs.
    
    Args:
        unique_ids: List of unique IDs. MUST be sorted for deterministic output.
    
    Returns:
        Report string with IDs in sorted order.
    """
    assert unique_ids == sorted(unique_ids), "IDs must be sorted!"
    return f"IDs: {', '.join(unique_ids)}"
```

## Technical Details

### Python's Hash Randomization

- **Purpose**: Prevent hash collision DoS attacks
- **Mechanism**: Randomizes hash seed per process
- **Environment Variable**: `PYTHONHASHSEED`
  - `-1` or unset: Random (default)
  - `0`: Disabled (deterministic, not recommended for production)
  - `N`: Fixed seed N

### When Set Order Appears Consistent

- ✅ Within same Python process (usually)
- ✅ With `PYTHONHASHSEED=0` (disabled randomization)
- ✅ Small sets with simple values (coincidental)
- ❌ Across different processes (almost never)
- ❌ In production environments (never rely on it)

### Alternatives to Sets

| Data Structure | Order | Duplicates | Use Case |
|----------------|-------|------------|----------|
| `set` | ❌ Undefined | ❌ No | Fast membership testing |
| `list` | ✅ Insertion | ✅ Yes | Ordered collection |
| `sorted(set)` | ✅ Sorted | ❌ No | Ordered unique values |
| `dict.fromkeys()` | ✅ Insertion (3.7+) | ❌ No | Ordered unique (preserves order) |

## Related Issues

This pattern appears in:
- String representation of sets
- JSON serialization of sets
- Hash generation from sets
- Logging set contents
- Database queries with `IN` clauses from sets
- Cache key generation from sets

## References

- [PEP 456: Secure and interchangeable hash algorithm](https://www.python.org/dev/peps/pep-0456/)
- [Python Docs: Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [Python Docs: PYTHONHASHSEED](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED)
- [Python Docs: sorted()](https://docs.python.org/3/library/functions.html#sorted)

---

**Status**: Known bug, intentionally left unfixed for educational purposes.

**Fix Available**: Yes, see `*_fixed()` functions in modules.

**Last Updated**: December 17, 2025
