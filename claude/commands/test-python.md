---
description: "Run Python tests with uv run pytest using haiku model"
argumentHint: "[test paths or pytest options] (e.g., tests/test_api.py -v -k specific_test)"
model: "haiku"
---

# Python Test Execution

Running Python tests: $ARGUMENTS

I'll execute `uv run pytest` with the haiku model for fast test execution.

## What I'll do:

1. Run `uv run pytest` with your specified arguments
2. Parse test results and failures
3. Provide a concise summary of:
   - Total tests run
   - Passed/failed/skipped counts
   - Any failure details with file:line references

## Usage examples:

- `/test-python` - Run all tests
- `/test-python tests/` - Run tests in tests directory
- `/test-python tests/test_api.py` - Run specific file
- `/test-python -v -k auth` - Run with verbose output, filter by "auth"
- `/test-python --lf` - Run last failed tests only

{Executing uv run pytest via Bash tool}
