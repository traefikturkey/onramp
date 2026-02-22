# CLI Design References

Resources used to audit and improve the OnRamp `make` command interface.

## Guidelines

- **[Command Line Interface Guidelines](https://clig.dev/)** — Community-driven guide covering help text, output, errors, arguments, flags, and more. The primary framework used for our CLI audit.

- **[12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)** — Jeff Dickey's principles for building CLI tools, covering configuration, error handling, stdout/stderr separation, and user experience.

- **[Atlassian CLI Design Principles](https://blog.developer.atlassian.com/10-design-principles-for-delightful-clis/)** — Atlassian's 10 design principles for building delightful command-line interfaces.

## Audit Summary

Scored against clig.dev and 12 Factor CLI guidelines: **4 pass / 12 partial / 11 fail** out of 27 criteria.

### Improvements Made

1. **Confirmation prompts on destructive operations** — `nuke-service`, `clean-acme`, `remove-etc`, `reset-database-folder`, `restore-backup`
2. **Post-action guidance** — `enable-service` prints next steps (edit-env, start-service, logs)
3. **Getting Started in help output** — `make help` shows a quick-start workflow
4. **Required variable validation** — `# required: VAR_NAME` convention in env templates warns on empty required vars during scaffold

### Remaining Opportunities

- Structured error output with consistent formatting
- Exit code standardization across make targets
- Machine-readable output option for scripting
- Tab completion support
- Color and formatting for terminal output
