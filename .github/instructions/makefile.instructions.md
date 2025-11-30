---
applyTo: "make.d/**/*.mk"
---
# Makefile Modules

See [shared context](../shared/makefile-modules.md) for patterns and conventions.

## Quick Reference
- Include pattern: `include make.d/*.mk`
- Always declare .PHONY for non-file targets
- Follow existing module patterns in make.d/
- Use SERVICE_PASSED_DNCASED for service name handling
