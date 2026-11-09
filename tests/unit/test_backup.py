"""Unit testy pro zálohování dat (příprava na pilot u zákazníka/design partnera).

Ověřují, že zálohovací služba vytváří archiv z konfigurovaných zdrojů,
respektuje nastavení šifrování a selhává bezpečně (fail-closed), když
šifrování nelze provést.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config.settings import Settings
from src.core.backup import (
    BACKUP_SOURCES,
    DEFAULT_ENCRYPTION_KEY,
    BackupService,
)

SOURCES = ("sqlite", "ledger", "vectors")


@pytest.fixture
def backup_env(tmp_path: Path) -> dict[str, Path]:
    """Dočasná datová a zálohová složka mimo repozitář (hermetické testy)."""
    return {
        "data_root": tmp_path / "data",
        "backup_dir": tmp_path / "backups",
    }


def _settings(env: dict[str, Path],
              encryption_key: str = DEFAULT_ENCRYPTION_KEY) -> Settings:
    return Settings(
        backup_dir=str(env["backup_dir"]),
        backup_encryption_key=encryption_key,
    )


def _create_source(env: dict[str, Path], name: str) -> None:
    (env["data_root"] / name).mkdir(parents=True, exist_ok=True)
    (env["data_root"] / name / "sample.txt").write_text(
        f"obsah {name}", encoding="utf-8"
    )


def test_backup_creates_archive_of_configured_sources(backup_env) -> None:
    for name in SOURCES:
        _create_source(backup_env, name)

    service = BackupService(
        _settings(backup_env), data_root=backup_env["data_root"]
    )
    result = service.create_backup()

    assert result.archive_path.exists()
    assert result.archive_path.suffix == ".gz"
    assert result.encrypted is False
    assert result.size_bytes > 0
    assert result.sources == SOURCES

    import tarfile  # lokálně, aby byl zřejmý účel

    with tarfile.open(result.archive_path, "r:gz") as tar:
        names = tar.getnames()
    assert any(name.startswith("sqlite") for name in names)
    assert any(name.startswith("ledger") for name in names)
    assert any(name.startswith("vectors") for name in names)


def test_backup_default_key_is_not_encrypted(backup_env) -> None:
    _create_source(backup_env, "sqlite")

    service = BackupService(
        _settings(backup_env), data_root=backup_env["data_root"]
    )
    result = service.create_backup()

    assert result.encrypted is False
    assert not Path(str(result.archive_path) + ".enc").exists()


def test_backup_real_key_marks_encrypted(backup_env, monkeypatch) -> None:
    _create_source(backup_env, "sqlite")
    settings = _settings(backup_env, encryption_key="real-production-key-123")
    service = BackupService(settings, data_root=backup_env["data_root"])

    encrypted_paths: list[str] = []

    def fake_encrypt(plain_path: Path) -> Path:
        encrypted_paths.append(str(plain_path))
        enc = Path(str(plain_path) + ".enc")
        enc.write_bytes(b"fake-encrypted")
        return enc

    monkeypatch.setattr(service, "_encrypt", fake_encrypt)
    result = service.create_backup()

    assert result.encrypted is True
    assert len(encrypted_paths) == 1
    assert str(result.archive_path).endswith(".enc")
    assert result.archive_path.exists()


def test_backup_real_key_without_openssl_raises(backup_env) -> None:
    """Fail-closed: reálný klíč + chybí openssl → chyba, žádná nešifrovaná záloha."""
    _create_source(backup_env, "sqlite")
    settings = _settings(backup_env, encryption_key="real-production-key-123")
    service = BackupService(settings, data_root=backup_env["data_root"])

    with pytest.raises(RuntimeError, match="Šifrování zálohy selhalo"):
        service.create_backup()


def test_backup_no_existing_sources_raises(backup_env) -> None:
    service = BackupService(
        _settings(backup_env), data_root=backup_env["data_root"]
    )
    with pytest.raises(RuntimeError, match="neexistuje"):
        service.create_backup()