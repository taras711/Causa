"""A3 ingestion pipeline – import a zpracování A3 dokumentů do znalostní báze.

Pipeline přijímá surový obsah (text, markdown, JSON), rozdělí jej na chunky,
vytvoří z nich FaceModel záznamy a naindexuje je pro hybridní retrieval.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config.settings import Settings
from src.models.face_model import FaceModelCreate, FaceModelResponse
from src.knowledge.retrieval import HybridRetriever


@dataclass
class IngestedChunk:
    """Jeden chunk vzniklý z ingestovaného dokumentu."""

    chunk_id: str
    source: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResult:
    """Výsledek celého ingestion běhu."""

    chunks: list[IngestedChunk] = field(default_factory=list)
    face_models: list[FaceModelResponse] = field(default_factory=list)
    indexed_documents: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class A3Ingestor:
    """Ingestuje A3 dokumenty (text, markdown, JSON) do znalostní báze.

    Každý chunk dokumentu může být uchován jako FaceModel záznam s mechanismem
    úspěchu, kontextem a tagy. Všechny dokumenty jsou naindexovány do
    HybridRetrieveru pro následné vyhledávání.
    """

    def __init__(
        self,
        retriever: HybridRetriever | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self.retriever = retriever or HybridRetriever()

    # ------------------------------------------------------------------ #
    # Veřejné rozhraní
    # ------------------------------------------------------------------ #

    def ingest_text(
        self,
        content: str,
        source: str,
        title: str | None = None,
        tenant_id: str = "default",
        create_face_models: bool = True,
    ) -> IngestionResult:
        """Ingestuje prostý textový obsah."""

        chunks = self._chunk_text(content, source=source, title=title or source)
        result = IngestionResult(chunks=chunks)

        if create_face_models:
            result.face_models = self._chunks_to_face_models(chunks, tenant_id)

        self._index_chunks(chunks, result)
        return result

    def ingest_markdown(
        self,
        content: str,
        source: str,
        title: str | None = None,
        tenant_id: str = "default",
        create_face_models: bool = True,
    ) -> IngestionResult:
        """Ingestuje markdown obsah (ignoruje formátování, zachovává text)."""

        plain = self._strip_markdown(content)
        chunks = self._chunk_text(plain, source=source, title=title or source)
        result = IngestionResult(chunks=chunks)

        if create_face_models:
            result.face_models = self._chunks_to_face_models(chunks, tenant_id)

        self._index_chunks(chunks, result)
        return result

    def ingest_json(
        self,
        content: str | dict[str, Any],
        source: str,
        title: str | None = None,
        tenant_id: str = "default",
        create_face_models: bool = True,
    ) -> IngestionResult:
        """Ingestuje JSON obsah (např. export A3 analýzy)."""

        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content

        # Extrakce textového obsahu z JSON struktury
        text_parts: list[str] = []
        self._extract_text_from_json(data, text_parts)
        plain = "\n".join(text_parts)

        chunks = self._chunk_text(plain, source=source, title=title or source)
        result = IngestionResult(chunks=chunks)

        if create_face_models:
            result.face_models = self._chunks_to_face_models(chunks, tenant_id)

        self._index_chunks(chunks, result)
        return result

    def ingest_file(
        self,
        path: str | Path,
        tenant_id: str = "default",
        create_face_models: bool = True,
    ) -> IngestionResult:
        """Ingestuje soubor z disku (přípona určuje formát)."""

        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            return IngestionResult(errors=[f"Soubor nenalezen: {file_path}"])

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return IngestionResult(errors=[f"Chyba při čtení souboru: {exc}"])
        source = str(file_path)
        title = file_path.stem

        suffix = file_path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            return self.ingest_markdown(
                content, source=source, title=title,
                tenant_id=tenant_id, create_face_models=create_face_models,
            )
        if suffix == ".json":
            return self.ingest_json(
                content, source=source, title=title,
                tenant_id=tenant_id, create_face_models=create_face_models,
            )
        # Výchozí: prostý text
        return self.ingest_text(
            content, source=source, title=title,
            tenant_id=tenant_id, create_face_models=create_face_models,
        )

    # ------------------------------------------------------------------ #
    # Interní pomocné metody
    # ------------------------------------------------------------------ #

    def _chunk_text(
        self,
        text: str,
        source: str,
        title: str,
        chunk_size: int = 800,
        overlap: int = 150,
    ) -> list[IngestedChunk]:
        """Rozdělí text na překrývající se chunky."""

        if not text.strip():
            return []

        # Rozdělení po odstavcích, poté po větách, pokud je odstavec příliš dlouhý
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len + 1 > chunk_size and current:
                chunks.append(" ".join(current))
                # Překrytí: ponechat poslední odstavce do dalšího chunku
                overlap_len = 0
                keep: list[str] = []
                for p in reversed(current):
                    if overlap_len + len(p) + 1 <= overlap:
                        keep.insert(0, p)
                        overlap_len += len(p) + 1
                    else:
                        break
                current = keep
                current_len = overlap_len
            current.append(para)
            current_len += para_len + 1

        if current:
            chunks.append(" ".join(current))

        return [
            IngestedChunk(
                chunk_id=f"{source}::chunk-{idx}",
                source=source,
                title=title,
                content=chunk,
                metadata={"source": source, "title": title},
            )
            for idx, chunk in enumerate(chunks)
        ]

    def _chunks_to_face_models(
        self,
        chunks: list[IngestedChunk],
        tenant_id: str,
    ) -> list[FaceModelResponse]:
        """Převádí chunky na FaceModelResponse záznamy."""

        face_models: list[FaceModelResponse] = []
        for chunk in chunks:
            # Pokus o extrakce mechanismu a kontextu z prvních slov chunku
            mechanism = self._extract_mechanism(chunk.content)
            company_context = f"{chunk.title} (zdroj: {chunk.source})"

            face_create = FaceModelCreate(
                name=chunk.title,
                company_context=company_context,
                mechanism=mechanism,
                evidence=chunk.source,
                applicable_to=[tenant_id],
                tags=["ingested", "a3"],
            )
            face_models.append(FaceModelResponse(**face_create.model_dump()))

        return face_models

    def _index_chunks(self, chunks: list[IngestedChunk], result: IngestionResult) -> None:
        """Naindexuje chunky do HybridRetrieveru."""

        for chunk in chunks:
            self.retriever.add_document(
                {
                    "id": chunk.chunk_id,
                    "title": chunk.title,
                    "content": chunk.content,
                    "source": chunk.source,
                    "metadata": chunk.metadata,
                }
            )
        result.indexed_documents = len(chunks)

    @staticmethod
    def _strip_markdown(content: str) -> str:
        """Odstraní markdown formátování (zjednodušeně)."""

        text = content
        # Odstranit nadpisovéマークy
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        # Odstranit tučné/kurzivníマークy
        text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text, flags=re.DOTALL)
        text = re.sub(r"(\*|_)(.*?)\1", r"\2", text, flags=re.DOTALL)
        # Odstranit odkazy, ponechat text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Odstranit kódové bloky
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Odstranit seznamníマークy
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        return text

    @staticmethod
    def _extract_text_from_json(data: Any, parts: list[str]) -> None:
        """Rekurzivně extrahuje všechny textové hodnoty z JSON."""

        if isinstance(data, dict):
            for value in data.values():
                A3Ingestor._extract_text_from_json(value, parts)
        elif isinstance(data, list):
            for item in data:
                A3Ingestor._extract_text_from_json(item, parts)
        elif isinstance(data, str):
            parts.append(data)
        elif isinstance(data, (int, float, bool)):
            parts.append(str(data))

    @staticmethod
    def _extract_mechanism(content: str) -> str:
        """Pokusí se z obsahu odvodit stručný mechanismus úspěchu."""

        first_sentence = content.split(".")[0].strip()
        if len(first_sentence) > 120:
            first_sentence = first_sentence[:120].rstrip() + "..."
        return first_sentence or "Mechanismus není z obsahu explicitně odvozen."