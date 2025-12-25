# flaky_deduplicator (Fixed)

This project contains a fixed version of the flaky deduplicator tool.

What changed
- The core fix is that unique IDs are returned and handled as a sorted list (deterministic order) instead of a `set`.
- Summary strings and report IDs are computed from deterministic summaries, so the same input always produces the same output across runs and processes.

Files of interest
- `src/deduplicator/deduplicator.py` — deterministic `deduplicate_records()`
- `src/deduplicator/reporter.py` — deterministic `generate_summary()` and `create_report()`
- `tests/test_deduplicator.py` — deterministic tests (no flaky markers)

Why this is deterministic
- Sets are inherently unordered and can iterate in different orders across processes because of hash randomization.
- The fix explicitly sorts unique IDs before producing strings and hashes, guaranteeing reproducible outputs.
