---
mode: "agent"
model: "gpt-5-mini"
description: "Run comprehensive quality checks: tests, linting, type checking. Fix failures systematically."
---

# Quality Check and Fix

## Objective

Run comprehensive quality gates and systematically address any failures until all checks pass.

## Context

This is the **primary quality gate** before committing code. All checks must pass.

**Priority:** Tests green > Lint clean > Types valid

---

## Workflow

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

**Result:**
- ✅ All tests pass → Proceed to Step 2
- ❌ Tests fail → Fix and re-run until green

### Step 2: Run Linting (Optional)

**Python (Ruff):**
```bash
uv run ruff check .
```

**Python (flake8):**
```bash
uv run flake8 src/ tests/
```

**JavaScript/TypeScript:**
```bash
npm run lint
```

**Result:**
- ✅ No lint errors → Proceed to Step 3
- ❌ Lint errors → Fix and re-run

### Step 3: Run Type Checking (Optional)

**Python (mypy):**
```bash
uv run mypy src/
```

**TypeScript:**
```bash
npm run type-check
```

**Result:**
- ✅ No type errors → All checks passed!
- ❌ Type errors → Fix and re-run

### Step 4: Run Makefile Target (If Available)

**If Makefile has a `check` target:**
```bash
make check
```

This typically runs all quality checks in sequence.

---

## Fixing Failures

### Test Failures

**Strategy:**
1. Read error messages carefully
2. Identify the root cause
3. Make minimal, targeted fixes
4. Re-run tests to verify fix
5. Repeat until all tests pass

**Common issues:**
- Import errors → Check `__init__.py` files, update imports
- Missing dependencies → `uv add --dev <package>`
- Deleted files → Update tests or remove obsolete test files
- Changed APIs → Update test expectations

**Example fix:**
```bash
# Error: ModuleNotFoundError: No module named 'requests'
uv add requests

# Re-run tests
uv run pytest -q
```

### Lint Failures

**Strategy:**
1. Auto-fix what's safe: `uv run ruff check --fix .`
2. Manually fix remaining issues
3. Re-run linter to verify

**Common issues:**
- Unused imports → Remove them
- Line too long → Break into multiple lines
- Missing docstrings → Add brief docstrings
- Code style → Run formatter: `uv run ruff format .`

### Type Errors

**Strategy:**
1. Add missing type hints
2. Fix incorrect type annotations
3. Use `# type: ignore` sparingly for genuinely complex cases
4. Prefer fixing the code over ignoring errors

**Common issues:**
- Missing type hints → Add them
- Incorrect types → Fix annotations
- Incompatible types → Adjust code or types

---

## Constraints

### From Repository Instructions

- ✅ Use `uv run pytest` for uv projects (never call `pytest` directly in uv projects)
- ✅ Make small, surgical fixes that preserve behavior
- ✅ Only add dependencies when explicitly required by failures
- ❌ Never add unnecessary flags: `uv run pytest` (not `uv run -m pytest`)
- ❌ Never prefix commands with `cd`
- ❌ Never add `|| true` to hide failures

### Best Practices

- **Prefer small changes** that preserve existing behavior
- **Fix root causes** rather than symptoms
- **Test frequently** - run tests after each fix
- **Keep commits clean** - all checks should pass before committing
- **Ask for clarification** if the fix is unclear or risky

---

## Example Sessions

### Example 1: Tests pass, lint has minor issues

```bash
# Step 1: Run tests
uv run pytest -q
# ✅ All tests pass

# Step 2: Run linter
uv run ruff check .
# ❌ Found 3 errors:
#   - Unused import 'sys' in src/main.py
#   - Line too long in src/utils.py
#   - Missing docstring in src/helpers.py

# Fix: Auto-fix safe issues
uv run ruff check --fix .
# ✅ Fixed 1 issue automatically

# Fix: Manually fix line length
# [Edit src/utils.py to break long line]

# Fix: Add docstring
# [Edit src/helpers.py to add docstring]

# Re-run linter
uv run ruff check .
# ✅ No errors found

# Report: All checks passed!
```

### Example 2: Test failures due to missing dependency

```bash
# Step 1: Run tests
uv run pytest -q
# ❌ Tests failed:
#   ModuleNotFoundError: No module named 'pydantic'

# Fix: Add missing dependency
uv add pydantic

# Re-run tests
uv run pytest -q
# ✅ All tests pass

# Step 2: Run linter
uv run ruff check .
# ✅ No errors found

# Report: All checks passed!
```

### Example 3: Complex test failure requiring code fix

```bash
# Step 1: Run tests
uv run pytest -q
# ❌ Tests failed:
#   test_user_service.py::test_create_user FAILED
#   AssertionError: Expected status 201, got 400

# Analyze: Check test and implementation
# [Read test_user_service.py]
# [Read user_service.py]

# Fix: Update validation logic in user_service.py
# [Edit user_service.py to fix validation]

# Re-run tests
uv run pytest -q
# ✅ All tests pass

# Continue with linting...
```

---

## Output Format

### Success Report

```
✅ Quality checks passed!

Tests: All passing
Lint: No errors
Types: All valid

Ready to commit.
```

### Failure Report

```
❌ Quality checks failed

Tests: 2 failing
  - test_auth.py::test_login - AssertionError
  - test_user.py::test_create - ValidationError

Fixes applied:
  - Added missing pydantic dependency
  - Updated test expectations

Re-running tests...
```

---

## Makefile Integration

### If `make check` exists:

Use it as the **final comprehensive gate** after individual checks pass:

```bash
# Run individual checks first
uv run pytest -q  # ✅
uv run ruff check .  # ✅

# Final comprehensive check
make check  # ✅

# Report: All checks passed!
```

### Makefile check target example:

```makefile
.PHONY: check
check: test lint type-check
	@echo "All checks passed!"
```

---

## Troubleshooting

### Tests hanging or taking too long

```bash
# Run with timeout
uv run pytest --timeout=60

# Run specific tests
uv run pytest tests/unit/ -k "fast"

# Skip slow tests
uv run pytest -m "not slow"
```

### Linter too strict

```bash
# Check what can be auto-fixed
uv run ruff check --fix .

# For specific rules to ignore, update pyproject.toml
```

### Type checker too strict

```bash
# Run with less strict checking
uv run mypy src/ --no-strict-optional

# Or add type: ignore comments strategically
```

---

## Customization Notes

**CUSTOMIZE THIS PROMPT** for your project:

1. **Test command:** Update for your test framework
2. **Linter:** ruff, flake8, eslint, etc.
3. **Type checker:** mypy, pyright, tsc
4. **Makefile:** Adjust if using different targets
5. **Quality gates:** Add/remove checks as needed
6. **CI alignment:** Match your CI/CD pipeline checks

**Source:** Consolidated from agent-spike, onboard, attempt-one
