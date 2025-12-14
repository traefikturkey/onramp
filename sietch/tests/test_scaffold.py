"""Tests for scaffold.py - path resolution and file filtering."""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scaffold import Scaffolder, IGNORE_PATTERNS
from tests.mocks.command import MockCommandExecutor
from ports.command import CommandResult


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


class TestRenderTemplate:
    """Tests for render_template() with Python-based templating."""

    def test_renders_template_successfully(self, tmp_path, monkeypatch):
        """Should render template with env var substitution."""
        monkeypatch.setenv("MY_VALUE", "hello_world")

        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "template.txt"
        source.write_text("VAR=${MY_VALUE}")

        dest = tmp_path / "output.txt"

        result = scaffolder.render_template(source, dest)

        assert result is True
        assert dest.exists()
        assert dest.read_text() == "VAR=hello_world"

    def test_substitutes_default_values(self, tmp_path):
        """Should use default value when env var is not set."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "template.txt"
        source.write_text("VAR=${UNSET_VAR:-default_value}")

        dest = tmp_path / "output.txt"

        scaffolder.render_template(source, dest)

        assert dest.read_text() == "VAR=default_value"

    def test_generates_password_for_unset_password_vars(self, tmp_path):
        """Should generate secure password for password-like variables."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "template.txt"
        source.write_text("PG_PASS=${PG_PASS}")

        dest = tmp_path / "output.txt"

        scaffolder.render_template(source, dest)

        content = dest.read_text()
        assert content.startswith("PG_PASS=")
        password = content.split("=", 1)[1]
        assert len(password) == 32  # Default password length
        assert "${" not in password

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories for output."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "template.txt"
        source.write_text("content")

        dest = tmp_path / "nested" / "dir" / "output.txt"

        result = scaffolder.render_template(source, dest)

        assert result is True
        assert dest.parent.exists()

    def test_handles_error_syntax(self, tmp_path, capsys):
        """Should warn and return empty for ${VAR:?error} syntax."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "template.txt"
        source.write_text("VAR=${REQUIRED_VAR:?must be set}")

        dest = tmp_path / "output.txt"

        result = scaffolder.render_template(source, dest)

        assert result is True
        assert dest.read_text() == "VAR="
        captured = capsys.readouterr()
        assert "REQUIRED_VAR not set" in captured.out

    def test_handles_missing_source_file(self, tmp_path, capsys):
        """Should handle missing source file gracefully."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "nonexistent.txt"
        dest = tmp_path / "output.txt"

        result = scaffolder.render_template(source, dest)

        assert result is False


class TestCopyStatic:
    """Tests for copy_static() - static file copying."""

    def test_copies_file(self, tmp_path):
        """Should copy file to destination."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "source.conf"
        source.write_text("static content")

        dest = tmp_path / "dest.conf"

        result = scaffolder.copy_static(source, dest)

        assert result is True
        assert dest.exists()
        assert dest.read_text() == "static content"

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories for destination."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "source.conf"
        source.write_text("content")

        dest = tmp_path / "nested" / "dir" / "dest.conf"

        result = scaffolder.copy_static(source, dest)

        assert result is True
        assert dest.parent.exists()
        assert dest.exists()

    def test_skips_existing_file(self, tmp_path, capsys):
        """Should not overwrite existing files (no-clobber)."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        source = tmp_path / "source.conf"
        source.write_text("new content")

        dest = tmp_path / "dest.conf"
        dest.write_text("existing content")

        result = scaffolder.copy_static(source, dest)

        assert result is True
        assert dest.read_text() == "existing content"
        captured = capsys.readouterr()
        assert "Skipped (exists)" in captured.out


class TestBuild:
    """Tests for build() - full scaffold build process."""

    def test_renders_templates(self, tmp_path):
        """Should render all templates for service."""
        mock_exec = MockCommandExecutor()
        mock_exec.set_response("envsubst", CommandResult(0, "rendered", ""))

        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create scaffold with template
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "env.template").write_text("VAR=${VALUE}")

        # Create services-enabled dir
        (tmp_path / "services-enabled").mkdir()

        result = scaffolder.build("plex")

        assert result is True
        # Check env file was created
        assert (tmp_path / "services-enabled" / "plex.env").exists()

    def test_copies_static_files(self, tmp_path):
        """Should copy static files for service."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create scaffold with static file
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "config.conf").write_text("static content")

        result = scaffolder.build("plex")

        assert result is True
        # Check static file was copied to etc/
        assert (tmp_path / "etc" / "plex" / "config.conf").exists()

    def test_returns_true_for_no_scaffold(self, tmp_path, capsys):
        """Should return True when no scaffold files exist."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        result = scaffolder.build("nonexistent")

        # Should succeed but print message
        captured = capsys.readouterr()
        assert "No scaffold templates" in captured.out

    def test_displays_message_on_success(self, tmp_path, capsys):
        """Should display MESSAGE.txt content on successful build."""
        mock_exec = MockCommandExecutor()
        mock_exec.set_response("envsubst", CommandResult(0, "rendered", ""))

        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create scaffold with template and message
        scaffold_dir = tmp_path / "services-scaffold" / "plex"
        scaffold_dir.mkdir(parents=True)
        (scaffold_dir / "env.template").write_text("VAR=${VALUE}")
        (scaffold_dir / "MESSAGE.txt").write_text("Please configure your Plex token!")

        (tmp_path / "services-enabled").mkdir()

        scaffolder.build("plex")

        captured = capsys.readouterr()
        assert "POST-ENABLE INSTRUCTIONS" in captured.out
        assert "Please configure your Plex token!" in captured.out


class TestTeardown:
    """Tests for teardown() - scaffold removal."""

    def test_removes_env_file(self, tmp_path):
        """Should remove service.env file."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create env file
        services_enabled = tmp_path / "services-enabled"
        services_enabled.mkdir()
        env_file = services_enabled / "plex.env"
        env_file.write_text("VAR=value")

        result = scaffolder.teardown("plex")

        assert result is True
        assert not env_file.exists()

    def test_preserves_etc_by_default(self, tmp_path):
        """Should preserve etc directory by default."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create etc directory
        etc_dir = tmp_path / "etc" / "plex"
        etc_dir.mkdir(parents=True)
        (etc_dir / "config.conf").write_text("content")

        (tmp_path / "services-enabled").mkdir()

        result = scaffolder.teardown("plex", preserve_etc=True)

        assert result is True
        assert etc_dir.exists()

    def test_removes_etc_when_requested(self, tmp_path):
        """Should remove etc directory when preserve_etc=False."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create etc directory
        etc_dir = tmp_path / "etc" / "plex"
        etc_dir.mkdir(parents=True)
        (etc_dir / "config.conf").write_text("content")

        (tmp_path / "services-enabled").mkdir()

        result = scaffolder.teardown("plex", preserve_etc=False)

        assert result is True
        assert not etc_dir.exists()


class TestIsVolumeDirectory:
    """Tests for _is_volume_directory() - volume path type detection."""

    def test_existing_directory_returns_true(self, tmp_path):
        """Should return True if path already exists as directory."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        abs_path = tmp_path / "etc" / "service" / "config"
        abs_path.mkdir(parents=True)

        result = scaffolder._is_volume_directory("service", "config", abs_path)
        assert result is True

    def test_existing_file_returns_false(self, tmp_path):
        """Should return False if path already exists as file."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        abs_path = tmp_path / "etc" / "service" / "config.yml"
        abs_path.parent.mkdir(parents=True)
        abs_path.write_text("content")

        result = scaffolder._is_volume_directory("service", "config.yml", abs_path)
        assert result is False

    def test_scaffold_directory_returns_true(self, tmp_path):
        """Should return True if scaffold source exists as directory."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        # Create scaffold directory
        scaffold_path = tmp_path / "services-scaffold" / "service" / "config"
        scaffold_path.mkdir(parents=True)

        abs_path = tmp_path / "etc" / "service" / "config"

        result = scaffolder._is_volume_directory("service", "config", abs_path)
        assert result is True

    def test_dot_d_suffix_returns_true(self, tmp_path):
        """Should return True for .d directory naming convention."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        abs_path = tmp_path / "etc" / "service" / "hosts.d"
        result = scaffolder._is_volume_directory("service", "hosts.d", abs_path)
        assert result is True

        abs_path = tmp_path / "etc" / "service" / "conf.d"
        result = scaffolder._is_volume_directory("service", "conf.d", abs_path)
        assert result is True

    def test_dot_available_suffix_returns_true(self, tmp_path):
        """Should return True for .available/.enabled directory naming convention."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        abs_path = tmp_path / "etc" / "service" / "sites.available"
        result = scaffolder._is_volume_directory("service", "sites.available", abs_path)
        assert result is True

        abs_path = tmp_path / "etc" / "service" / "mods.enabled"
        result = scaffolder._is_volume_directory("service", "mods.enabled", abs_path)
        assert result is True

    def test_file_extension_returns_false(self, tmp_path):
        """Should return False for common file extensions."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        file_extensions = ["config.yml", "config.yaml", "settings.conf",
                           "data.json", "data.xml", "settings.ini", "readme.txt"]

        for filename in file_extensions:
            abs_path = tmp_path / "etc" / "service" / filename
            result = scaffolder._is_volume_directory("service", filename, abs_path)
            assert result is False, f"Expected False for {filename}"

    def test_no_extension_returns_true(self, tmp_path):
        """Should return True for paths without extension (assumed directory)."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        abs_path = tmp_path / "etc" / "service" / "data"
        result = scaffolder._is_volume_directory("service", "data", abs_path)
        assert result is True

        abs_path = tmp_path / "etc" / "service" / "cache"
        result = scaffolder._is_volume_directory("service", "cache", abs_path)
        assert result is True


class TestScaffolderInit:
    """Tests for Scaffolder initialization."""

    def test_uses_injected_executor(self, tmp_path):
        """Should use injected command executor."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(str(tmp_path), executor=mock_exec)

        assert scaffolder._executor is mock_exec

    def test_default_base_dir(self):
        """Should use /app as default base directory."""
        mock_exec = MockCommandExecutor()
        scaffolder = Scaffolder(executor=mock_exec)

        assert scaffolder.base_dir == Path("/app")
