"""Tests for Proxmox external instance generation and migration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from external_instances import (  # noqa: E402
    GENERATED_HEADER,
    ExternalInstancesError,
    generate,
    migrate,
    read_dotenv,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


@pytest.fixture
def base(tmp_path: Path) -> Path:
    (tmp_path / "services-enabled").mkdir()
    (tmp_path / "external-enabled").mkdir()
    write(tmp_path / "services-enabled" / ".env", "HOST_DOMAIN=example.test\n")
    return tmp_path


def load_generated(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith(GENERATED_HEADER)
    return yaml.safe_load(text.removeprefix(GENERATED_HEADER))


class TestGenerate:
    def test_generate_single_and_multiple_instances(self, base: Path) -> None:
        write(
            base / "services-enabled" / "proxmox.external.yml",
            "instances:\n"
            "  zed:\n"
            "    host_name: zed\n"
            "    address: pve-zed\n"
            "  proxmox:\n"
            "    host_name: proxmox\n"
            "    address: 192.168.1.50\n",
        )

        output = generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)

        assert "created generated active config" in output
        data = load_generated(base / "external-enabled" / "proxmox.yml")
        assert list(data["http"]["routers"]) == ["proxmox", "zed"]
        router = data["http"]["routers"]["proxmox"]
        assert router == {
            "rule": "Host(`proxmox.example.test`)",
            "entrypoints": ["websecure"],
            "middlewares": ["default-headers"],
            "tls": {},
            "service": "proxmox",
        }
        assert data["http"]["services"]["proxmox"] == {
            "loadBalancer": {
                "passHostHeader": True,
                "servers": [{"url": "https://192.168.1.50:8006/"}],
            }
        }

    def test_generate_uses_instance_fqdn_over_domain(self, base: Path) -> None:
        write(
            base / "services-enabled" / "proxmox.external.yml",
            "instances:\n  proxmox:\n    fqdn: pve.lan.test\n    address: pve\n",
        )

        generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)

        data = load_generated(base / "external-enabled" / "proxmox.yml")
        assert data["http"]["routers"]["proxmox"]["rule"] == "Host(`pve.lan.test`)"

    @pytest.mark.parametrize(
        ("content", "message"),
        [
            ("instances:\n  Bad_Key:\n    host_name: pve\n    address: 1.2.3.4\n", "invalid instance key"),
            ("instances:\n  pve:\n    address: 1.2.3.4\n", "missing host_name"),
            ("instances:\n  pve:\n    host_name: pve\n", "missing address"),
            ("instances:\n  pve:\n    host_name: 'p`ve'\n    address: 1.2.3.4\n", "invalid host_name"),
            ("instances:\n  pve:\n    host_name: pve\n    address: https://1.2.3.4\n", "invalid address"),
            ("instances:\n  a:\n    fqdn: pve.example.test\n    address: a\n  b:\n    fqdn: pve.example.test\n    address: b\n", "duplicate FQDN"),
        ],
    )
    def test_invalid_records_fail_before_writing(self, base: Path, content: str, message: str) -> None:
        write(base / "services-enabled" / "proxmox.external.yml", content)

        with pytest.raises(ExternalInstancesError, match=message):
            generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)

        assert not (base / "external-enabled" / "proxmox.yml").exists()

    def test_missing_domain_fails_when_no_instance_domain_or_fqdn(self, tmp_path: Path) -> None:
        write(
            tmp_path / "services-enabled" / "proxmox.external.yml",
            "instances:\n  proxmox:\n    host_name: proxmox\n    address: 192.168.1.50\n",
        )

        with pytest.raises(ExternalInstancesError, match="domain is required"):
            generate("proxmox", tmp_path, dry_run=False, force=False, replace_unmanaged=False)

    def test_overwrite_safety_and_replace_backup(self, base: Path) -> None:
        write(base / "services-enabled" / "proxmox.external.yml", "instances:\n  proxmox:\n    fqdn: pve.example.test\n    address: pve\n")
        active = base / "external-enabled" / "proxmox.yml"
        write(active, "# operator owned\n")

        with pytest.raises(ExternalInstancesError, match="unmanaged active"):
            generate("proxmox", base, dry_run=False, force=True, replace_unmanaged=False)

        output = generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=True)

        assert "backed up unmanaged active" in output
        assert (base / "external-enabled" / "proxmox.yml.bak").read_text() == "# operator owned\n"
        assert active.read_text(encoding="utf-8").startswith(GENERATED_HEADER)

    def test_deterministic_generate_bytes(self, base: Path) -> None:
        write(base / "services-enabled" / "proxmox.external.yml", "instances:\n  proxmox:\n    fqdn: pve.example.test\n    address: pve\n")
        generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        first = (base / "external-enabled" / "proxmox.yml").read_bytes()
        generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        assert (base / "external-enabled" / "proxmox.yml").read_bytes() == first
        assert b"\r\n" not in first

    def test_unsupported_service_has_no_side_effects(self, base: Path) -> None:
        before = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        with pytest.raises(ExternalInstancesError, match="supported for: proxmox"):
            generate("truenas", base, dry_run=False, force=False, replace_unmanaged=False)
        after = sorted(str(path.relative_to(base)) for path in base.rglob("*"))
        assert after == before


class TestMigrate:
    def test_migrate_main_style_without_env_mutation(self, base: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=proxmox\nPROXMOX_ADDRESS=192.168.1.50\n")
        original_env = dict(os.environ)

        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)

        assert dict(os.environ) == original_env
        data = yaml.safe_load((base / "services-enabled" / "proxmox.external.yml").read_text())
        assert data == {
            "managed_by": "onramp-migration",
            "instances": {"proxmox": {"host_name": "proxmox", "address": "192.168.1.50"}},
        }

    def test_migrate_indexed_and_incomplete_pair_failure(self, base: Path) -> None:
        write(
            base / "services-enabled" / ".env.external",
            "PROXMOX_HOST_NAME=proxmox\nPROXMOX_ADDRESS=192.168.1.50\n"
            "PROXMOX2_HOST_NAME=pve2\nPROXMOX2_ADDRESS=192.168.1.51\n",
        )
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        text = (base / "services-enabled" / "proxmox.external.yml").read_text()
        assert text.index("proxmox:") < text.index("proxmox2:")

        write(base / "services-enabled" / ".env.external", "PROXMOX3_HOST_NAME=orphan\n")
        with pytest.raises(ExternalInstancesError, match="incomplete legacy Proxmox pair"):
            migrate("proxmox", base, dry_run=True, force=False, replace_unmanaged=False)

    def test_migration_idempotent_and_managed_update_requires_force(self, base: Path) -> None:
        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=proxmox\nPROXMOX_ADDRESS=192.168.1.50\n")
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        first = (base / "services-enabled" / "proxmox.external.yml").read_bytes()
        assert "up to date" in migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        assert (base / "services-enabled" / "proxmox.external.yml").read_bytes() == first

        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=proxmox\nPROXMOX_ADDRESS=192.168.1.60\n")
        with pytest.raises(ExternalInstancesError, match="managed source conflict"):
            migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        migrate("proxmox", base, dry_run=False, force=True, replace_unmanaged=False)
        assert "192.168.1.60" in (base / "services-enabled" / "proxmox.external.yml").read_text()

    def test_unmanaged_source_requires_replace_and_backup(self, base: Path) -> None:
        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=proxmox\nPROXMOX_ADDRESS=192.168.1.50\n")
        source = base / "services-enabled" / "proxmox.external.yml"
        write(source, "instances:\n  user:\n    fqdn: user.example.test\n    address: user\n")

        with pytest.raises(ExternalInstancesError, match="unmanaged source"):
            migrate("proxmox", base, dry_run=False, force=True, replace_unmanaged=False)

        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=True)
        assert (base / "services-enabled" / "proxmox.external.yml.bak").exists()
        assert yaml.safe_load(source.read_text())["managed_by"] == "onramp-migration"

    def test_dotenv_grammar_and_domain_precedence(self, base: Path) -> None:
        write(base / "services-enabled" / ".env", "HOST_DOMAIN=from-env.test\n")
        write(
            base / "services-enabled" / ".env.external",
            "# comment\r\n\r\nexport PROXMOX_HOST_NAME='pve'\r\nPROXMOX_ADDRESS=\"192.168.1.50\"\r\n",
        )
        assert read_dotenv(base / "services-enabled" / ".env.external")["PROXMOX_HOST_NAME"] == "pve"
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        data = load_generated(base / "external-enabled" / "proxmox.yml")
        assert data["http"]["routers"]["proxmox"]["rule"] == "Host(`pve.from-env.test`)"

        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=pve # nope\nPROXMOX_ADDRESS=1.2.3.4\n")
        with pytest.raises(ExternalInstancesError, match="inline comments"):
            migrate("proxmox", base, dry_run=True, force=False, replace_unmanaged=False)

    def test_migrate_deterministic_bytes(self, base: Path) -> None:
        write(base / "services-enabled" / ".env.external", "PROXMOX2_HOST_NAME=pve2\nPROXMOX2_ADDRESS=host2\nPROXMOX_HOST_NAME=pve1\nPROXMOX_ADDRESS=host1\n")
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        first = (base / "services-enabled" / "proxmox.external.yml").read_bytes()
        assert first.startswith(b"managed_by: onramp-migration\ninstances:\n")
        assert b"\r\n" not in first
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        assert (base / "services-enabled" / "proxmox.external.yml").read_bytes() == first

    def test_migration_output_can_feed_generator(self, base: Path) -> None:
        write(base / "services-enabled" / ".env.external", "PROXMOX_HOST_NAME=pve\nPROXMOX_ADDRESS=192.168.1.50\n")
        migrate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        generate("proxmox", base, dry_run=False, force=False, replace_unmanaged=False)
        assert "pve.example.test" in (base / "external-enabled" / "proxmox.yml").read_text()

    def test_unsupported_migrate_no_side_effects(self, base: Path) -> None:
        with pytest.raises(ExternalInstancesError, match="supported for: proxmox"):
            migrate("truenas", base, dry_run=False, force=False, replace_unmanaged=False)
        assert not (base / "services-enabled" / "truenas.external.yml").exists()
