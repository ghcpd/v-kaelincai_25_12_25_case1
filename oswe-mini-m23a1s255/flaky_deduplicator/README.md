# Data Deduplicator — Fixed (deterministic)

This folder contains a fixed version of the `flaky_deduplicator` demo. The
original (buggy) implementation returned a `set` of IDs and relied on set
iteration order when building summary strings — this produced non-deterministic
outputs across processes and caused flaky tests.

What was fixed
- deduplicate_records(): now returns a SORTED list of unique IDs (deterministic)
- generate_summary()/create_report(): normalize and sort IDs before use
- tests: removed xfail/flaky markers and assert deterministic outputs

Why this is safe
- API compatibility is preserved at a high level (same function names and
  behavior). `unique_ids` is now a list (keeps membership/len semantics) but is
  deterministic.
- The fix eliminates reliance on Python's hash randomization and makes
  summaries and report IDs stable across runs and processes.

How determinism is enforced
- All outputs that depend on a collection of IDs are generated from a
  sorted list of string IDs (sorted(..., key=str)).

Running the fixed tests

```powershell
cd v-kaelincai_25_12_25_case1\fixed_project\flaky_deduplicator
pytest -q
```

Expected result: all tests pass consistently across runs and processes.
