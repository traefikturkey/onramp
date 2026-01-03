# Implementation Checklist: Anonymous Analytics

**PRD:** `docs/prd-anonymous-analytics.md`
**Branch:** `feature/anonymous-analytics`

---

## Phase 1: Foundation

### 1.1 PostHog Setup
- [ ] Create PostHog Cloud account
- [ ] Create OnRamp project in PostHog
- [ ] Obtain project API key
- [ ] Document API key environment variable (`POSTHOG_API_KEY`)

### 1.2 Lock File Implementation
- [ ] Create `onramp.lock` in project root (key=value format)
- [ ] Create Python module for lock file management
- [ ] Implement UUID generation on first use
- [ ] Implement `ANALYTICS_ENABLED` flag storage
- [ ] Implement `ANALYTICS_NOTICE_SHOWN` flag storage
- [ ] Add `onramp.lock` to `.gitignore`

### 1.3 Analytics Core Module
- [ ] Add `posthog` to Python dependencies
- [ ] Create `sietch/scripts/analytics.py` (or integrate into existing module)
- [ ] Implement `get_analytics_id()` function
- [ ] Implement `is_analytics_enabled()` function
- [ ] Implement `track_event(event, properties)` function
- [ ] Add sync mode and GeoIP disable configuration
- [ ] Add graceful error handling (analytics failures should never break commands)

---

## Phase 2: Opt-In Mechanism

### 2.1 Enable/Disable Options
- [ ] Support `ONRAMP_ANALYTICS_ENABLED=1` environment variable
- [ ] Store enabled state in `onramp.lock`

### 2.2 Make Commands
- [ ] Add `make analytics-status` command
- [ ] Add `make analytics-enable` command (shows one-time notice)
- [ ] Add `make analytics-disable` command
- [ ] Add `make analytics-show-id` command
- [ ] Add `make analytics-reset-id` command

---

## Phase 3: Event Integration

### 3.1 Service Events
- [ ] Track `service_enabled` in `make enable-service`
- [ ] Track `service_disabled` in `make disable-service`
- [ ] Track `service_started` in `make start-service`
- [ ] Track `service_stopped` in `make stop-service`
- [ ] Track `service_restarted` in `make restart-service`
- [ ] Track `service_nuked` in `make nuke-service`

### 3.2 Override Events
- [ ] Track `override_enabled` in `make enable-override`
- [ ] Track `override_disabled` in `make disable-override`

### 3.3 Command Events
- [ ] Track `command_executed` for key make targets
- [ ] Track `error_occurred` for command failures
- [ ] Include `success` boolean property
- [ ] Include `duration_ms` property (optional)

### 3.4 Scaffold Events
- [ ] Track `scaffold_built` in `make scaffold-build`

---

## Phase 4: User Communication

### 4.1 First-Run Notice
- [ ] Implement first-run detection (check lock file existence)
- [ ] Create notice text
- [ ] Display notice on first tracked command
- [ ] Mark notice as shown (in lock file or separate marker)

### 4.2 Documentation
- [ ] Create `docs/analytics.md` user-facing documentation
- [ ] Document what data is collected
- [ ] Document opt-out methods
- [ ] Document privacy guarantees
- [ ] Add link to analytics docs in README (optional)

---

## Phase 5: Testing & Validation

### 5.1 Unit Tests
- [ ] Test `get_analytics_id()` generates valid UUID
- [ ] Test `get_analytics_id()` returns same ID on subsequent calls
- [ ] Test `is_analytics_enabled()` returns False by default
- [ ] Test `is_analytics_enabled()` respects `ONRAMP_ANALYTICS_ENABLED` env var
- [ ] Test `is_analytics_enabled()` respects lock file setting
- [ ] Test `track_event()` handles PostHog errors gracefully
- [ ] Test lock file read/write operations

### 5.2 Integration Tests
- [ ] Test analytics doesn't break commands when PostHog is unreachable
- [ ] Test analytics doesn't significantly slow down commands
- [ ] Test opt-out actually prevents event sending

### 5.3 Manual Verification
- [ ] Verify events appear in PostHog dashboard
- [ ] Verify no PII is captured
- [ ] Verify GeoIP is disabled (no location data)
- [ ] Verify anonymous mode (no person profiles created)

---

## Phase 6: Rollout

### 6.1 Pre-Release
- [ ] Review all tracked properties for PII
- [ ] Security review of API key handling
- [ ] Update CHANGELOG
- [ ] Create PR with detailed description

### 6.2 Release
- [ ] Merge to main
- [ ] Monitor PostHog for initial events
- [ ] Verify error rates in analytics

### 6.3 Post-Release
- [ ] Create initial dashboard in PostHog
- [ ] Set up alerts for unusual patterns
- [ ] Gather feedback from users

---

## Decision Log

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Lock file location | Project root vs services-enabled | **Project root** (`onramp.lock`) | Visible, easy to find |
| Lock file format | YAML vs key=value | **key=value** | Shell compatibility |
| Default state | Opt-in vs opt-out | **Opt-in** (disabled by default) | Privacy-first approach |
| Service name tracking | Actual names vs categories | **Actual names** | More actionable insights |
| API key storage | Env var vs hardcoded vs config | **Environment variable** | Standard practice, configurable |

---

## Notes

- Analytics failures must NEVER break user commands
- All tracking code should be wrapped in try/except
- Consider timeout on PostHog calls to prevent hangs
- Use sync_mode=True for CLI but with short timeout
