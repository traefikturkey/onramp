---
mode: "agent"
model: "gpt-5-mini"
description: "Run tests, report failures, and fix issues. Use /check for comprehensive quality checks."
---

# Run Tests

## Objective

Run the test suite and systematically fix any failures until all tests pass.

---

## Execution

### Step 1: Run Tests

**Python (uv):**
```bash
uv run pytest -q
```

**Python (traditional):**
```bash
pytest
```

**Node.js:**
```bash
npm test
```

**Ruby:**
```bash
bundle exec rspec
```

**Go:**
```bash
go test ./...
```

### Step 2: Analyze Failures

If tests fail:
1. **Read error messages carefully**
2. **Identify the root cause**
3. **Determine the fix**
4. **Apply the fix**
5. **Re-run tests**
6. **Repeat until green**

---

## Common Test Failures

### Import/Module Errors

**Error:** `ModuleNotFoundError: No module named 'package'`

**Fix:**
```bash
# For uv projects
uv add package

# For traditional pip
pip install package
```

**Error:** `ImportError: cannot import name 'function' from 'module'`

**Fix:**
- Check if function exists in module
- Update import statement
- Check `__init__.py` exports

### Assertion Failures

**Error:** `AssertionError: Expected X, got Y`

**Fix:**
- Understand what the test expects
- Check if implementation matches expectation
- Update implementation OR update test (if expectation changed)

### File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'file.txt'`

**Fix:**
- Check if file path is correct
- Ensure file exists in test fixtures
- Create missing test data files

### Deleted Module Tests

**Error:** Test file tries to import deleted module

**Fix:**
```python
# Move skip() to TOP of test file, before imports
import pytest
pytest.skip("Module removed", allow_module_level=True)

# Imports below won't be evaluated
from deleted_module import Something
```

**Or:** Delete the obsolete test file entirely

---

## Test Output Formats

### Quiet Mode (Recommended for Quick Checks)
```bash
uv run pytest -q
```

**Output:**
```
........F..
```
- `.` = passed
- `F` = failed
- `E` = error

### Verbose Mode (For Detailed Information)
```bash
uv run pytest -v
```

**Output:**
```
tests/test_user.py::test_create_user PASSED
tests/test_user.py::test_update_user FAILED
tests/test_auth.py::test_login PASSED
```

### Short Traceback (For Cleaner Errors)
```bash
uv run pytest --tb=short
```

Shows condensed traceback, easier to read.

---

## Selective Test Running

### Run Specific File
```bash
uv run pytest tests/test_user.py -v
```

### Run Specific Test
```bash
uv run pytest tests/test_user.py::test_create_user -v
```

### Run Tests Matching Pattern
```bash
uv run pytest -k "user" -v
# Runs all tests with "user" in the name
```

### Run Tests by Marker
```bash
uv run pytest -m "not slow" -v
# Skip tests marked as slow
```

---

## Fixing Strategy

### 1. Collection Errors

**Issue:** pytest can't collect tests

**Common causes:**
- Syntax errors in test files
- Import errors
- Missing `__init__.py` in test directories

**Fix:**
1. Check syntax
2. Fix imports
3. Add `__init__.py` if needed

### 2. Setup/Teardown Errors

**Issue:** Fixture setup fails

**Fix:**
1. Check fixture definition
2. Verify dependencies exist
3. Ensure resources are available

### 3. Test Logic Errors

**Issue:** Test expectations don't match implementation

**Fix:**
1. Understand what test expects
2. Verify implementation is correct
3. Update test OR implementation (prefer fixing implementation)

---

## Constraints

### From Repository Instructions

- ✅ Use `uv run pytest` for uv projects (never call `pytest` directly)
- ✅ Make minimal, targeted fixes
- ✅ Preserve existing behavior
- ❌ Never add unnecessary flags: `uv run pytest` (not `uv run -m pytest`)
- ❌ Never skip tests without good reason
- ❌ Never commit with failing tests

---

## Example Session

### Example 1: Import error fix

```bash
# Run tests
uv run pytest -q
# ❌ E..........
#
# ERROR: ModuleNotFoundError: No module named 'pydantic'

# Fix: Add missing dependency
uv add pydantic

# Re-run tests
uv run pytest -q
# ✅ ........... (all passed)
```

### Example 2: Assertion failure fix

```bash
# Run tests
uv run pytest -v
# ❌ tests/test_user.py::test_create_user FAILED
#    AssertionError: assert 400 == 201

# Analyze: Test expects 201, got 400
# [Read test file and implementation]

# Fix: Update validation in user_service.py
# [Edit user_service.py]

# Re-run tests
uv run pytest -v
# ✅ tests/test_user.py::test_create_user PASSED
```

### Example 3: Deleted module test

```bash
# Run tests
uv run pytest -q
# ❌ E..........
#
# ERROR: ImportError: cannot import name 'OldClass' from 'old_module'

# Fix: Skip test file for deleted module
# Edit tests/test_old_module.py:
# Add at TOP:
import pytest
pytest.skip("Module removed", allow_module_level=True)

# Re-run tests
uv run pytest -q
# ✅ ........... (skipped old tests, rest passed)
```

---

## When to Use /test vs /check

### Use `/test` when:
- You just want to run tests quickly
- You're iterating on test fixes
- Tests are your primary concern

### Use `/check` when:
- You want comprehensive quality checks (tests + lint + types)
- You're preparing to commit
- You need full validation

**Recommendation:** Use `/test` during development, `/check` before committing.

---

## Coverage (Optional)

### Run with coverage:
```bash
uv run pytest --cov=src --cov-report=html --cov-report=term
```

### View coverage report:
```bash
open htmlcov/index.html
```

### Minimum coverage (if configured):
```bash
uv run pytest --cov=src --cov-fail-under=80
```

---

## Output Format

### Success Report
```
✅ All tests passed!

Tests run: 45
Passed: 45
Failed: 0
Skipped: 0
```

### Failure Report
```
❌ Tests failed

Failed tests:
  - tests/test_user.py::test_create_user
  - tests/test_auth.py::test_login

Fixing...
```

### After Fix
```
✅ All tests passed!

Fixes applied:
  - Added missing pydantic dependency
  - Updated validation logic in user_service.py
```

---

## Troubleshooting

### Tests hanging

```bash
# Add timeout
uv run pytest --timeout=60
```

### Too many tests running

```bash
# Run only unit tests
uv run pytest tests/unit/ -v

# Skip slow tests
uv run pytest -m "not slow"
```

### Confusing output

```bash
# Use short traceback
uv run pytest --tb=short

# Or line-based output
uv run pytest --tb=line
```

---

## Customization Notes

**CUSTOMIZE THIS PROMPT** for your project:

1. **Test command:** pytest, jest, rspec, go test, etc.
2. **Test organization:** Update paths for your structure
3. **Markers:** Add project-specific test markers
4. **Coverage:** Set minimum coverage requirements
5. **CI alignment:** Match CI/CD test commands

**Source:** Consolidated from agent-spike, onboard, attempt-one
