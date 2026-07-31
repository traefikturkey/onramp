"""Tests for dashboard icon resolution."""

import pytest

from dashboard.core.icons import (
    FALLBACK_ICON,
    get_icon_url,
    resolve_icon_filename,
)


class TestResolveIconFilename:
    """Tests for resolve_icon_filename."""

    def test_manual_override(self):
        """Should use explicit manual override."""
        upstream = {"actual-budget", "docker"}
        assert resolve_icon_filename("actual", upstream) == "actual-budget"

    def test_exact_match(self):
        """Should match service name exactly when present upstream."""
        upstream = {"plex", "docker"}
        assert resolve_icon_filename("plex", upstream) == "plex"

    def test_suffix_stripping(self):
        """Should strip known suffixes to find a match."""
        upstream = {"gitea", "docker"}
        assert resolve_icon_filename("gitea-runner", upstream) == "gitea"

    def test_suffix_stripping_with_manual_override(self):
        """Should use manual override on stripped prefix."""
        upstream = {"adguard-home", "docker"}
        assert resolve_icon_filename("adguard", upstream) == "adguard-home"

    def test_fallback_when_no_match(self):
        """Should fall back to docker icon when nothing matches."""
        upstream = {"docker"}
        assert resolve_icon_filename("unknown-service", upstream) == FALLBACK_ICON

    def test_empty_upstream(self):
        """Should fallback when upstream set is empty."""
        assert resolve_icon_filename("anything", set()) == FALLBACK_ICON


class TestGetIconUrl:
    """Tests for get_icon_url."""

    def test_returns_local_static_path(self):
        """Should return local static icon path."""
        assert get_icon_url("plex") == "/static/icons/plex.svg"

    def test_normalizes_name(self):
        """Should normalize service name to lowercase."""
        assert get_icon_url("Plex") == "/static/icons/plex.svg"

    def test_strips_whitespace(self):
        """Should strip whitespace from service name."""
        assert get_icon_url("  plex  ") == "/static/icons/plex.svg"
