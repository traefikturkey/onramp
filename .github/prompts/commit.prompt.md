---
mode: "agent"
model: "gpt-5-mini"
description: "Create logical git commits with security scanning. Add 'push' to also push after committing."
---

# Commit Workflow

You are a meticulous repository assistant. Create atomic, logical commits with security scanning.

## Step 1: Check Status

```bash
git status --short
```

- If working tree is clean → Report "No changes to commit" and exit
- If merge conflicts exist → Report conflicts and exit (user must resolve first)

---

## Step 2: Check for Encrypted Files

If `.gitattributes` exists, parse lines with `filter=git-crypt` to identify encrypted file patterns. Skip these files during security scanning (they're encrypted before pushing).

---

## Step 3: Security Scan

**CRITICAL:** Scan all non-encrypted modified and untracked files for secrets.

**Secret patterns to detect:**

| Category | Patterns |
|----------|----------|
| Secret files | `.env`, `credentials.json`, `secrets.yaml`, `*.pem`, `*.key`, `*.p12`, `*.pfx` |
| AWS keys | `AKIA`, `ABIA`, `ACCA`, `ASIA` prefixes |
| GitHub tokens | `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` |
| Anthropic keys | `sk-ant-` |
| OpenAI keys | `sk-proj-`, `sk-` |
| Generic API keys | `API_KEY=`, `APIKEY=`, `api_key=` |
| Tokens | `TOKEN=`, `ACCESS_TOKEN=`, `Bearer` |
| Passwords | `PASSWORD=`, `pwd=`, `passwd=`, `secret=` |
| Private keys | `-----BEGIN PRIVATE KEY-----`, `-----BEGIN RSA`, `-----BEGIN OPENSSH` |
| Connection strings | `mongodb://`, `postgres://`, `mysql://` |

**If secrets found:** STOP immediately. Show details and suggest adding to `.gitignore`. Do NOT proceed.

---

## Step 4: Categorize Files

### Auto-ignore (add to .gitignore):
- `*.log`, `*.csv`, `*.tsv`
- `*.db`, `*.sqlite`, `*.sqlite3`
- Large data files (`*.json` over 1MB, `*.xml` data dumps)

### Auto-stage for commit:
- Source code: `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, etc.
- Documentation: `*.md`, `*.rst`, `*.txt`
- Configuration: `pyproject.toml`, `package.json`, `Dockerfile`, `docker-compose.yml`, `*.yml`, `*.yaml`
- Test files

### Ask user about:
- Ambiguous data files (could be fixtures or user data)
- Binary files not in `.gitignore`
- Unclear file types

When asking, use batch prompting: "Track these files? (y/n/pattern)" where pattern allows specifying a `.gitignore` rule.

---

## Step 5: Group by Logical Change

Group related files into atomic commits using these types:

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code restructuring |
| `perf` | Performance improvements |
| `style` | Formatting changes |
| `chore` | Maintenance tasks |
| `build` | Build system changes |
| `ci` | CI/CD changes |
| `deps` | Dependency updates |
| `revert` | Undo previous commit |

**Rules:**
- Related functionality changes go together
- Don't mix unrelated changes
- Each commit should do ONE thing (atomic commits)

---

## Step 6: Create Commits

For each group of related files:

1. **Stage files:**
   ```bash
   git add <files>
   ```

2. **Write commit message:**
   - Human-style with natural grammar
   - NO emojis in commit messages
   - Brief summary line (≤72 chars, imperative mood)
   - Optional detailed body

3. **Use HEREDOC for multi-line messages:**
   ```bash
   git commit -m "$(cat <<'EOF'
   type: summary line here

   Optional detailed body explaining WHAT and WHY.
   Wrap at 72 characters.
   EOF
   )"
   ```

4. **Create the commit**

5. **Check status again:**
   ```bash
   git status --short
   ```

6. **Repeat** if legitimate files remain (not matching auto-ignore patterns)

---

## Step 7: Exit Loop When

- Working tree is clean
- Only files matching `.gitignore` patterns remain
- User says to stop when prompted about unclear files

---

## Step 8: Summary

Show a brief summary of commits created:
```
Created 3 commits:
  abc1234 feat(auth): add JWT token validation
  def5678 docs: update API documentation
  ghi9012 chore: update dependencies
```

---

## Step 9: Push (Optional)

**Only if `${input:push}` contains "push":**
```bash
git push
```

Otherwise, stop after creating commits without pushing.

---

## Constraints

- ❌ Never push without explicit "push" instruction
- ❌ Never commit if secrets are detected
- ❌ Never commit if no changes exist
- ❌ Never commit with merge conflicts
- ❌ Never use emojis in commit messages
- ❌ Never mix unrelated changes in one commit

---

## Examples

### Example 1: Single feature commit

```bash
# Check status
git status --short
# M src/auth.py
# M tests/test_auth.py

# Security scan - clean

# Group: Both files relate to auth feature
git add src/auth.py tests/test_auth.py

# Commit
git commit -m "$(cat <<'EOF'
feat(auth): add password hashing

Implements bcrypt password hashing for user registration.
Adds salt rounds configuration via environment variable.
EOF
)"

# Summary
# Created 1 commit:
#   abc1234 feat(auth): add password hashing
```

### Example 2: Multiple atomic commits

```bash
# Check status
git status --short
# M README.md
# M src/utils.py
# A tests/test_utils.py
# M pyproject.toml

# Security scan - clean

# Group 1: Utils changes
git add src/utils.py tests/test_utils.py
git commit -m "refactor(utils): extract date formatting helper"

# Group 2: Docs
git add README.md
git commit -m "docs: update installation instructions"

# Group 3: Dependencies
git add pyproject.toml
git commit -m "deps: bump pydantic to 2.5.0"

# Summary
# Created 3 commits:
#   abc1234 refactor(utils): extract date formatting helper
#   def5678 docs: update installation instructions
#   ghi9012 deps: bump pydantic to 2.5.0
```

### Example 3: Secrets detected

```bash
# Check status
git status --short
# M src/config.py
# A .env

# Security scan
# ❌ SECRETS DETECTED:
#   .env - Contains API_KEY=sk-proj-xxxxx
#
# Action: Add .env to .gitignore
# Do NOT commit until secrets are removed or ignored.
```

---

## Customization Notes

**CUSTOMIZE THIS PROMPT** for your project:

1. **Secret patterns:** Add project-specific secrets to scan for
2. **Auto-ignore patterns:** Adjust for your data files
3. **Commit types:** Add project-specific types if needed
4. **HEREDOC format:** Adjust if your shell differs

**Source:** Consolidated from Claude Code and Copilot templates
