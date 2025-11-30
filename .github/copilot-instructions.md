# OnRamp

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Primary Context

Full project context is in [.claude/CLAUDE.md](../.claude/CLAUDE.md) (shared with Claude Code).

## Copilot-Specific Resources

- **Path-scoped instructions**: `.github/instructions/*.instructions.md`
- **Shared context**: `.github/shared/*.md` (sietch, makefiles, scaffolding)
- **Chat modes**: `.github/chatmodes/*.chatmode.md`
- **Prompt templates**: `.github/prompts/*.prompt.md`

## Quick Reference

| Task | Command |
|------|---------|
| Enable service | `make enable-service NAME` |
| Start service | `make start-service NAME` |
| View logs | `make logs NAME` |
| List services | `make list-services` |
| Edit config | `make edit-env NAME` |

## Guardrails

- Do not create files without explicit user request
- Always use `make` commands, never raw `docker compose`
- Commit all changes when asked (clean `git status`)
