---
mode: "agent"
model: "gpt-5-mini"
description: "Run linting checks and fix issues. Use /check for comprehensive quality checks including tests."
---

# Lint Code

## Objective

Run linting checks and systematically fix issues until code is clean.

---

## Execution

### Step 1: Run Linter

**Python (Ruff - Recommended):**
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
# or
npx eslint .
```

**Go:**
```bash
golangci-lint run
```

### Step 2: Auto-fix Safe Issues

**Ruff:**
```bash
uv run ruff check --fix .
```

**ESLint:**
```bash
npm run lint -- --fix
```

### Step 3: Manually Fix Remaining Issues

Review remaining issues and fix them one by one.

### Step 4: Re-run Linter

Verify all issues are resolved:
```bash
uv run ruff check .
# Should show: All checks passed!
```

---

## Common Linting Issues

### Unused Imports

**Error:** `F401 [*] 'sys' imported but unused`

**Fix:** Remove the unused import
```python
# Before
import sys
import os

# After
import os
```

### Line Too Long

**Error:** `E501 Line too long (95 > 88 characters)`

**Fix:** Break into multiple lines
```python
# Before
result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)

# After
result = some_function(
    arg1, arg2, arg3, arg4,
    arg5, arg6, arg7, arg8
)
```

### Missing Docstrings

**Error:** `D100 Missing docstring in public module`

**Fix:** Add docstring
```python
# Before
def calculate_total(items):
    return sum(item.price for item in items)

# After
def calculate_total(items):
    """Calculate total price of all items."""
    return sum(item.price for item in items)
```

### Undefined Names

**Error:** `F821 Undefined name 'User'`

**Fix:** Add missing import
```python
# Before
def get_user():
    return User()

# After
from app.models import User

def get_user():
    return User()
```

### Formatting Issues

**Error:** Multiple formatting violations

**Fix:** Run formatter
```bash
uv run ruff format .
# or
uv run black .
```

---

## Linter Configuration

### Ruff (pyproject.toml)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "D100",  # Missing docstring in public module
    "D103",  # Missing docstring in public function
]
```

### ESLint (.eslintrc.json)

```json
{
  "extends": ["eslint:recommended"],
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

---

## Selective Linting

### Lint Specific File
```bash
uv run ruff check src/main.py
```

### Lint Specific Directory
```bash
uv run ruff check src/
```

### Ignore Specific Rules
```python
# Ignore specific rule for one line
result = long_function_call()  # noqa: E501

# Ignore all rules for one line
result = complex_code()  # noqa

# Ignore specific rule for whole file (at top)
# ruff: noqa: E501
```

---

## Fixing Strategy

### 1. Auto-fix First
```bash
# Let the linter fix what it can
uv run ruff check --fix .

# Check what's left
uv run ruff check .
```

### 2. Group Similar Issues
```bash
# See all issues grouped
uv run ruff check . | grep "F401"  # All unused imports
```

### 3. Fix Systematically
- Fix all unused imports
- Fix all line length issues
- Add missing docstrings
- Fix naming issues

### 4. Verify Clean
```bash
uv run ruff check .
# All checks passed!
```

---

## Integration with Formatter

### Run Formatter First
```bash
# Format code
uv run ruff format .

# Then check for remaining issues
uv run ruff check .
```

### Combined Workflow
```bash
# Format and fix in one go
uv run ruff format . && uv run ruff check --fix .
```

---

## Constraints

### From Repository Instructions

- ✅ Use `uv run ruff` for uv projects
- ✅ Make minimal, targeted fixes
- ✅ Auto-fix safe issues
- ❌ Never suppress all warnings without review
- ❌ Never commit with linting errors (unless explicitly ignored)

---

## Example Sessions

### Example 1: Auto-fix cleans everything

```bash
# Run linter
uv run ruff check .
# ❌ Found 12 errors (5 auto-fixable)

# Auto-fix
uv run ruff check --fix .
# Fixed 5 errors

# Re-check
uv run ruff check .
# ✅ All checks passed!
```

### Example 2: Manual fixes needed

```bash
# Run linter
uv run ruff check .
# ❌ Found 8 errors:
#   - F401: 'sys' imported but unused (x3)
#   - E501: Line too long (x5)

# Auto-fix imports
uv run ruff check --fix .
# Fixed 3 errors (removed unused imports)

# Manually fix line length
# [Edit files to break long lines]

# Re-check
uv run ruff check .
# ✅ All checks passed!
```

### Example 3: Add missing docstrings

```bash
# Run linter
uv run ruff check .
# ❌ Found 10 errors:
#   - D100: Missing docstring in public module (x10)

# Add docstrings to files
# [Edit files to add module docstrings]

# Re-check
uv run ruff check .
# ✅ All checks passed!
```

---

## When to Use /lint vs /check

### Use `/lint` when:
- You just want to check code style
- You're fixing formatting issues
- You're iterating on code cleanup

### Use `/check` when:
- You want tests + lint + types
- You're preparing to commit
- You need full validation

**Recommendation:** Use `/lint` during cleanup, `/check` before committing.

---

## Output Format

### Success Report
```
✅ Linting passed!

Files checked: 25
Issues found: 0
Auto-fixed: 0
```

### Failure Report
```
❌ Linting failed

Issues found: 8
  - Unused imports: 3
  - Line too long: 5

Applying auto-fixes...
```

### After Fix
```
✅ Linting passed!

Fixes applied:
  - Removed 3 unused imports
  - Reformatted 5 long lines
```

---

## Troubleshooting

### Too many errors

```bash
# Focus on specific error types
uv run ruff check . | grep "F401"

# Fix one type at a time
uv run ruff check --select F401 .
```

### Conflicting rules

```bash
# Run formatter to standardize
uv run ruff format .

# Then lint
uv run ruff check .
```

### Performance issues

```bash
# Lint only changed files
git diff --name-only | xargs uv run ruff check
```

---

## Pre-commit Integration

### Setup pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Install hooks
```bash
pre-commit install
```

---

## Customization Notes

**CUSTOMIZE THIS PROMPT** for your project:

1. **Linter:** ruff, flake8, eslint, golangci-lint, etc.
2. **Rules:** Configure which rules to enforce
3. **Ignores:** Set project-specific ignores
4. **Auto-fix:** Define what can be auto-fixed
5. **Integration:** Add to CI/CD pipeline

**Source:** Consolidated from agent-spike, onboard, attempt-one
