"""Tests for scaffold.py - path resolution and file filtering."""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scaffold import Scaffolder, IGNORE_PATTERNS


class TestIgnorePatterns:
    """Tests for IGNORE_PATTERNS constant."""

    def test_md_files_ignored(self):
        assert "*.md" in IGNORE_PATTERNS

    def test_gitkeep_ignored(self):
        assert ".gitkeep" in IGNORE_PATTERNS

    def test_scaffold_manifest_ignored(self):
        assert "scaffold.yml" in IGNORE_PATTERNS

    def test_message_file_ignored(self):
        assert "MESSAGE.txt" in IGNORE_PATTERNS


class TestShouldIgnore:
    """Tests for _should_ignore() - file filtering."""

    def test_ignores_md_files(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("README.md")) is True
        assert scaffolder._should_ignore(Path("docs/INSTALL.md")) is True

    def test_ignores_gitkeep(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path(".gitkeep")) is True

    def test_ignores_scaffold_manifest(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("scaffold.yml")) is True

    def test_ignores_message_file(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("MESSAGE.txt")) is True

    def test_allows_templates(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("config.yml.template")) is False

    def test_allows_config_files(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("config.yml")) is False
        assert scaffolder._should_ignore(Path("settings.json")) is False

    def test_allows_static_files(self):
        scaffolder = Scaffolder.__new__(Scaffolder)
        assert scaffolder._should_ignore(Path("config.conf")) is False
        assert scaffolder._should_ignore(Path("data.xml")) is False


class TestGetOutputPath:
    """Tests for get_output_path() - output path calculation."""

    def test_env_template_goes_to_services_enabled(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "plex" / "env.template"
        result = scaffolder.get_output_path("plex", source)

        assert result == tmp_path / "services-enabled" / "plex.env"

    def test_other_template_goes_to_etc(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "plex" / "config.xml.template"
        result = scaffolder.get_output_path("plex", source)

        assert result == tmp_path / "etc" / "plex" / "config.xml"

    def test_static_file_goes_to_etc(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "plex" / "settings.json"
        result = scaffolder.get_output_path("plex", source)

        assert result == tmp_path / "etc" / "plex" / "settings.json"

    def test_nested_path_preserved(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "plex" / "subdir" / "config.yml"
        result = scaffolder.get_output_path("plex", source)

        assert result == tmp_path / "etc" / "plex" / "subdir" / "config.yml"

    def test_nested_template_preserved(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "plex" / "subdir" / "config.yml.template"
        result = scaffolder.get_output_path("plex", source)

        assert result == tmp_path / "etc" / "plex" / "subdir" / "config.yml"

    def test_onramp_env_goes_to_services_enabled(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "onramp" / ".env.template"
        result = scaffolder.get_output_path("onramp", source)

        assert result == tmp_path / "services-enabled" / ".env"

    def test_onramp_env_nfs_goes_to_services_enabled(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "onramp" / ".env.nfs.template"
        result = scaffolder.get_output_path("onramp", source)

        assert result == tmp_path / "services-enabled" / ".env.nfs"

    def test_onramp_env_external_goes_to_services_enabled(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "onramp" / ".env.external.template"
        result = scaffolder.get_output_path("onramp", source)

        assert result == tmp_path / "services-enabled" / ".env.external"

    def test_onramp_other_files_go_to_etc(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))

        source = tmp_path / "services-scaffold" / "onramp" / "config.yml"
        result = scaffolder.get_output_path("onramp", source)

        assert result == tmp_path / "etc" / "onramp" / "config.yml"


class TestFindScaffoldFiles:
    """Tests for find_scaffold_files() - file discovery."""

    def test_finds_templates(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "env.template").write_text("VAR=${VALUE}")
        (scaffold_dir / "config.yml.template").write_text("key: ${VALUE}")

        scaffolder = Scaffolder(str(tmp_path))
        templates, statics = scaffolder.find_scaffold_files("plex")

        assert len(templates) == 2
        template_names = [t.name for t in templates]
        assert "env.template" in template_names
        assert "config.yml.template" in template_names

    def test_finds_statics(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "config.conf").write_text("static content")
        (scaffold_dir / "data.json").write_text("{}")

        scaffolder = Scaffolder(str(tmp_path))
        templates, statics = scaffolder.find_scaffold_files("plex")

        assert len(statics) == 2
        static_names = [s.name for s in statics]
        assert "config.conf" in static_names
        assert "data.json" in static_names

    def test_excludes_ignored_files(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "config.conf").write_text("static")
        (scaffold_dir / "README.md").write_text("documentation")
        (scaffold_dir / ".gitkeep").write_text("")
        (scaffold_dir / "scaffold.yml").write_text("operations: []")

        scaffolder = Scaffolder(str(tmp_path))
        templates, statics = scaffolder.find_scaffold_files("plex")

        static_names = [s.name for s in statics]
        assert "config.conf" in static_names
        assert "README.md" not in static_names
        assert ".gitkeep" not in static_names
        assert "scaffold.yml" not in static_names

    def test_finds_nested_files(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        subdir = scaffold_dir / "subdir"
        subdir.mkdir(parents=True)
        (subdir / "nested.template").write_text("${VAR}")
        (subdir / "nested.conf").write_text("static")

        scaffolder = Scaffolder(str(tmp_path))
        templates, statics = scaffolder.find_scaffold_files("plex")

        assert len(templates) == 1
        assert templates[0].name == "nested.template"
        assert len(statics) == 1
        assert statics[0].name == "nested.conf"

    def test_returns_empty_for_missing_service(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))
        templates, statics = scaffolder.find_scaffold_files("nonexistent")

        assert templates == []
        assert statics == []


class TestFindManifest:
    """Tests for find_manifest() - scaffold.yml discovery."""

    def test_finds_manifest(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "scaffold.yml").write_text("version: '1'")

        scaffolder = Scaffolder(str(tmp_path))
        result = scaffolder.find_manifest("plex")

        assert result is not None
        assert result.name == "scaffold.yml"

    def test_returns_none_when_missing(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)

        scaffolder = Scaffolder(str(tmp_path))
        result = scaffolder.find_manifest("plex")

        assert result is None


class TestHasScaffold:
    """Tests for has_scaffold() - scaffold existence check."""

    def test_true_with_templates(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "env.template").write_text("VAR=${VALUE}")

        scaffolder = Scaffolder(str(tmp_path))
        assert scaffolder.has_scaffold("plex") is True

    def test_true_with_statics(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "config.conf").write_text("content")

        scaffolder = Scaffolder(str(tmp_path))
        assert scaffolder.has_scaffold("plex") is True

    def test_true_with_manifest(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "scaffold.yml").write_text("version: '1'")

        scaffolder = Scaffolder(str(tmp_path))
        assert scaffolder.has_scaffold("plex") is True

    def test_false_with_only_ignored_files(self, tmp_path):
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "README.md").write_text("docs")
        (scaffold_dir / ".gitkeep").write_text("")

        scaffolder = Scaffolder(str(tmp_path))
        # scaffold.yml is not present, and README.md/.gitkeep are ignored
        assert scaffolder.has_scaffold("plex") is False

    def test_false_when_missing(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))
        assert scaffolder.has_scaffold("nonexistent") is False


class TestListScaffolds:
    """Tests for list_scaffolds() - available scaffold listing."""

    def test_lists_scaffolds(self, tmp_path):
        scaffold_base = tmp_path / "services-scaffold"
        (scaffold_base / "plex").mkdir(parents=True)
        (scaffold_base / "radarr").mkdir(parents=True)
        (scaffold_base / "sonarr").mkdir(parents=True)

        scaffolder = Scaffolder(str(tmp_path))
        result = scaffolder.list_scaffolds()

        assert result == ["plex", "radarr", "sonarr"]

    def test_returns_sorted(self, tmp_path):
        scaffold_base = tmp_path / "services-scaffold"
        (scaffold_base / "zebra").mkdir(parents=True)
        (scaffold_base / "alpha").mkdir(parents=True)

        scaffolder = Scaffolder(str(tmp_path))
        result = scaffolder.list_scaffolds()

        assert result == ["alpha", "zebra"]

    def test_empty_when_no_scaffold_dir(self, tmp_path):
        scaffolder = Scaffolder(str(tmp_path))
        result = scaffolder.list_scaffolds()

        assert result == []
