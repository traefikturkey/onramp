# PRD: Anonymous Analytics for OnRamp

**Status:** Draft
**Branch:** `feature/anonymous-analytics`
**Author:** [TBD]
**Created:** 2026-01-03

---

## Overview

Add opt-in anonymous analytics to OnRamp to understand usage patterns without collecting personally identifiable information.

## Problem Statement

OnRamp currently has no visibility into:
- Which services are most commonly enabled
- Which overrides are used
- What commands users run most frequently
- Common error patterns or friction points

This data would help prioritize development efforts and identify areas for improvement.

## Goals

1. **Anonymous**: No PII collected; cannot identify individual users or their infrastructure
2. **Opt-in/Opt-out**: Users can easily disable analytics
3. **Transparent**: Users can see exactly what data is collected
4. **Minimal**: Only collect data that provides actionable insights
5. **Non-intrusive**: Zero impact on command performance or reliability

## Non-Goals

- User identification or tracking across machines
- Collecting hostnames, domains, or IP addresses
- Collecting service configuration details
- Collecting file paths or environment variable values
- Session replay or detailed usage patterns

---

## Solution: PostHog Integration

### Why PostHog?

- Open-source with self-hosted option
- Cloud free tier: 1M events/month
- Native anonymous event support (no person profiles)
- Python SDK suitable for CLI applications
- GDPR-compliant data handling

### Data Collection

#### Events to Track

| Event | Properties | Purpose |
|-------|------------|---------|
| `service_enabled` | `service_name`, `has_scaffold` | Understand service popularity |
| `service_disabled` | `service_name` | Track service churn |
| `override_enabled` | `override_name` | Understand override usage |
| `override_disabled` | `override_name` | Track override churn |
| `command_executed` | `command`, `success`, `duration_ms` | Identify common workflows |
| `error_occurred` | `command`, `error_type` | Find friction points |

#### Properties Never Collected

- Hostname or domain name
- IP address (GeoIP disabled)
- File paths
- Environment variable values
- Service configuration
- Error messages containing user data

### Anonymous Identification

Generate a random UUID stored in `onramp.lock` (or similar):

```
# onramp.lock
analytics_id=550e8400-e29b-41d4-a716-446655440000
```

**Purpose**: Deduplication and aggregate analysis only. This ID:
- Cannot be linked to a person
- Cannot be linked to infrastructure
- Provides consistent tracking for trend analysis
- Can be regenerated at any time by deleting the file

### Opt-In Mechanism

Analytics are **disabled by default**. Users can enable via:

1. **Environment variable**: `ONRAMP_ANALYTICS_ENABLED=1`
2. **Make command**: `make analytics-enable` / `make analytics-disable`

When enabled, a one-time notice is shown explaining what data is collected.

---

## Technical Design

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Make Command  │────▶│  Python Wrapper  │────▶│  PostHog Cloud  │
│                 │     │  (sietch/...)    │     │  (anonymous)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   onramp.lock    │
                        │  (analytics_id)  │
                        └──────────────────┘
```

### Implementation Options

#### Option A: Python Module in Sietch
- Add `sietch/scripts/analytics.py`
- Call from Makefile targets via `python sietch/scripts/analytics.py track <event>`
- Pros: Consistent with existing architecture
- Cons: Adds subprocess call to each command

#### Option B: Makefile Integration
- Source analytics functions in Makefile
- Use `curl` to send events directly to PostHog API
- Pros: No Python dependency per command
- Cons: More complex Makefile, curl may not handle batching well

#### Option C: Hook-Based Wrapper
- Wrap `docker compose` commands with analytics layer
- Pros: Captures all operations automatically
- Cons: More invasive, harder to control what's tracked

**Recommended**: Option A (Python module) for consistency and maintainability.

### PostHog Configuration

```python
from posthog import Posthog

posthog = Posthog(
    api_key="phc_xxx",  # From environment or config
    host="https://us.i.posthog.com",
    sync_mode=True,      # CLI apps need sync mode
    disable_geoip=True   # Privacy: no IP-based location
)
```

### Lock File Format

Location: `/apps/onramp/onramp.lock` (project root)

Key=value format for shell compatibility:
```
ANALYTICS_ID=550e8400-e29b-41d4-a716-446655440000
ANALYTICS_NOTICE_SHOWN=1
```

---

## User Experience

### First Run Notice

Shown once after user enables analytics:

```
Analytics enabled. OnRamp collects anonymous usage statistics to improve the project.
No personal data or infrastructure details are collected.

To disable: make analytics-disable
To learn more: https://github.com/xxx/onramp/docs/analytics.md
```

### Commands

```bash
make analytics-status    # Show current analytics state
make analytics-disable   # Disable analytics
make analytics-enable    # Enable analytics
make analytics-show-id   # Show current analytics ID
make analytics-reset-id  # Generate new analytics ID
```

---

## Privacy Considerations

### Data Minimization
- Only collect event names and minimal properties
- Never collect configuration values
- Strip any potentially identifying information

### Transparency
- Document exactly what is collected
- Provide commands to view collected data
- Open-source the analytics code

### User Control
- Easy opt-out mechanism
- Ability to reset/regenerate analytics ID
- No penalties or reduced functionality for opting out

### Data Retention
- Use PostHog's default retention (1 year)
- No need for longer retention for aggregate analytics

---

## Decisions

| Question | Decision |
|----------|----------|
| Lock file location | `onramp.lock` in project root |
| Default state | **Opt-in** (disabled by default) |
| Service names | Track actual service names |
| First-run notice | Show once (after user enables analytics) |
| API key storage | Environment variable |

## Open Questions

1. **Self-hosted option**: Should we support users running their own PostHog instance?

---

## Success Metrics

- Track adoption rate (users with analytics enabled)
- Identify top 10 most-enabled services
- Identify top 10 most-used commands
- Track error rates by command type
- Monitor average command execution times

---

## Implementation Checklist

See `docs/implementation-checklist-analytics.md` for detailed implementation steps.

---

## References

- [PostHog Python SDK](https://posthog.com/docs/libraries/python)
- [PostHog Anonymous Events](https://posthog.com/docs/data/anonymous-vs-identified-events)
- [PostHog Privacy](https://posthog.com/docs/privacy)
