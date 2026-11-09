"""Šifrované zálohování datových souborů (SQLite, ledger, vektory).

Záloha se řídí nastavením z `Settings`:
* ``backup_dir`` – kam se archivy ukládají (výchozí ``./data/backups``),
* ``backup_encryption_key`` – klíč pro AES-256 šifrování; výchozí
  ``change-in-production`` znamená „nezálohovat šifrovaně“ (vývoj).

Archiv se vytváří pomocí `tarfile` ze standardní knihovny. Volitelné
šifrování probíhá přes `openssl` (AES-256-CBC), konzistentně s
`infrastructure/backups/backup_script.sh` určeným pro kontejnerové nasazení.

Pouze lokální souborový systém – žádné externí cloudové zálohy.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Výchozí (nezabezpečená) hodnota klíče – při ní se záloha nešifruje.
DEFAULT_ENCRYPTION_KEY = "change-in-production"

# Datové adresáře pod `data/`, které se standardně zálohují.
BACKUP_SOURCES: tuple[str, ...] = ("sqlite", "ledger", "vectors")


@dataclass
class BackupResult:
    """Výsledek běhu zálohování."""

    archive_path: Path
    encrypted: bool
    size_bytes: int
    created_at: str
    sources: tuple[str, ...]


class BackupService:
    """Vytváří časově razítkované, volitelně šifrované zálohy dat."""

    def __init__(
        self,
        settings: Settings,
        data_root: str | Path | None = None,
    ) -> None:
        self.settings = settings
        self.backup_dir = Path(settings.backup_dir)
        self.encryption_key = settings.backup_encryption_key or ""
        self._data_root = (
            Path(data_root) if data_root is not None
            else Path(__file__).resolve().parents[2] / "data"
        )

    def create_backup(
        self, sources: tuple[str, ...] = BACKUP_SOURCES
    ) -> BackupResult:
        """Vytvoří zálohu vybraných datových zdrojů.

        :raises RuntimeError: když žádný zdroj neexistuje, nebo když je
            vyžadováno šifrování, ale není k dispozici `openssl`.
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        existing = [
            source for source in sources
            if (self._data_root / source).exists()
        ]
        if not existing:
            raise RuntimeError(
                "Žádný ze zálohovaných zdrojů v adresáři data/ neexistuje."
            )

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"causa_backup_{timestamp}.tar.gz"
        plain_path = self.backup_dir / archive_name

        self._create_tar(plain_path, existing)
        logger.info("Zálohovací archiv vytvořen: %s", plain_path)

        if self._should_encrypt():
            final_path = self._encrypt(plain_path)
            encrypted = True
        else:
            logger.warning(
                "Záloha není šifrovaná (nastavte reálný BACKUP_ENCRYPTION_KEY pro produkci)."
            )
            final_path = plain_path
            encrypted = False

        return BackupResult(
            archive_path=final_path,
            encrypted=encrypted,
            size_bytes=final_path.stat().st_size,
            created_at=timestamp,
            sources=tuple(existing),
        )

    def _create_tar(self, output: Path, sources: list[str]) -> None:
        with tarfile.open(output, "w:gz") as tar:
            for source in sources:
                tar.add(self._data_root / source, arcname=source)

    def _should_encrypt(self) -> bool:
        return bool(
            self.encryption_key
            and self.encryption_key != DEFAULT_ENCRYPTION_KEY
        )

    def _encrypt(self, plain_path: Path) -> Path:
        """Zašifruje archiv přes `openssl` a odstraní nešifrovanou kopii."""
        encrypted_path = Path(str(plain_path) + ".enc")
        env = os.environ.copy()
        env["BACKUP_ENCRYPTION_KEY"] = self.encryption_key
        try:
            subprocess.run(
                [
                    "openssl", "enc", "-aes-256-cbc", "-salt",
                    "-in", str(plain_path),
                    "-out", str(encrypted_path),
                    "-pass", "env:BACKUP_ENCRYPTION_KEY",
                ],
                check=True,
                capture_output=True,
                env=env,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            plain_path.unlink(missing_ok=True)
            raise RuntimeError(f"Šifrování zálohy selhalo: {exc}") from exc
        plain_path.unlink(missing_ok=True)
        return encrypted_path


def main() -> None:
    """CLI vstupní bod (např. `python -m src.core.backup`)."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s"
    )
    service = BackupService(Settings())
    try:
        result = service.create_backup()
        logger.info(
            "Záloha vytvořena: %s (šifrovaná=%s, %s B, zdroje: %s)",
            result.archive_path,
            result.encrypted,
            result.size_bytes,
            ", ".join(result.sources),
        )
    except RuntimeError as exc:
        logger.error("Zálohování selhalo: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()