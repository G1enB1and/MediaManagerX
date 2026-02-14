# Dev Workflow (Phase 1)

## Setup
```bash
make setup
```

## Test
```bash
make test
```

## Smoke run
```bash
make run
```

## What `make test` does
- Runs full unit test suite (`tests/test_*.py`) via `python3 scripts/dev_check.py`
- Exits non-zero on failure for easy CI/automation use
