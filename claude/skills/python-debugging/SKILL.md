---
name: python-debugging
description: Hypothesis-driven Python debugging methodology with structured deliverables. This skill should be used when debugging Python bugs, tracing unexpected behavior, or diagnosing data pipeline issues. Provides systematic investigation patterns and pandas-specific debugging checklists.
---

# Python Debugging

Systematic debugging methodology for Python, with emphasis on hypothesis-driven investigation and structured deliverables.

## Core Loop: Hypothesis-Driven Investigation

1. **Enumerate hypotheses** - List all possible causes based on error and context
2. **Design minimal experiment** - Create smallest test to validate/invalidate one hypothesis
3. **Execute and log** - Run experiment, record exact outcome
4. **Prune systematically** - Eliminate disproven hypotheses
5. **Iterate** - Repeat until root cause identified

## Pandas Data Flow Checklist

At each transformation step, check:

- **Shape**: rows × columns before and after
- **Dtypes**: unexpected type coercion (int→float from NaN, object from mixed types)
- **Nulls**: null counts per column, where they appear
- **Index**: alignment issues after merge/join, duplicate indices
- **Unique keys**: cardinality changes, unexpected duplicates
- **Memory**: implicit copies from chained assignment (`df[col][mask] = val` vs `df.loc[mask, col] = val`)

## Scratch Scripts

Create debugging scripts in `.scratch/` directory (git-ignored):

- `.scratch/debug_dataframe_nans.py`
- `.scratch/profile_memory.py`
- `.scratch/reproduce_issue.py`

Include reproduction steps as comments. Keep until bug is fully resolved.

## Debugging Commands

```bash
uv run pytest -v --tb=short          # Verbose with short tracebacks
uv run pytest --pdb                  # Drop into debugger on failure
uv run pytest -x                     # Stop on first failure
uv run python -m cProfile script.py  # CPU profiling
uv run python -m pdb script.py       # Interactive debugging
```

## Required Deliverables

Every debugging session concludes with:

1. **Repro Recipe** - Step-by-step instructions to reproduce
2. **Root Cause** - Clear explanation of why the bug occurs
3. **Minimal Patch** - Smallest code change that fixes the issue
4. **Regression Test** - Test case that would have caught this bug
5. **Verification** - Steps to confirm fix works

## Common Python Gotchas

- Mutable default arguments (`def f(x=[])` → use `None` sentinel)
- Late binding closures in loops → capture with default arg
- `is` vs `==` for value comparison
- Integer interning (`a is b` works for small ints, fails for large)
- Import cycles causing `None` attributes
- `except Exception` swallowing `KeyboardInterrupt`/`SystemExit`
