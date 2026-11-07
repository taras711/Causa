"""Verifikační vrstva – ověření tvrzení proti WorkModelu, datům klienta, předpokladům a FaceModel vzorům."""
from __future__ import annotations

from typing import Any


class VerificationLayer:
    """Ověřuje tvrzení a přiřazuje úroveň: unverified / partial / verified.

    Zdroje pravdy:
      - work_model – schválené pracovní modely firmy
      - client_data – data klienta
      - assumption – explicitně označený předpoklad (vždy jen 'partial')
      - face_model – ověřený vzor z FaceModel knowledge base
    """

    def __init__(
        self,
        work_model: dict[str, Any] | None = None,
        face_models: list[dict[str, Any]] | None = None,
    ) -> None:
        self.work_model = work_model or {}
        self.face_models = face_models or []

    def verify(self, claim: dict[str, Any]) -> dict[str, Any]:
        """Vrátí verifikační výsledek pro dané tvrzení.

        Očekávané klíče v claim:
          - text: text tvrzení
          - source: work_model | client_data | assumption | face_model
          - evidence: volitelné odkazy na důkazy
          - face_model_id: volitelné ID FaceModelu pro verifikaci proti vzoru
        """
        text = claim.get("text", "")
        source = claim.get("source", "assumption")
        evidence = claim.get("evidence")
        face_model_id = claim.get("face_model_id")

        if source == "assumption":
            return {
                "verified": False,
                "level": "partial",
                "notes": "Tvrzení je založeno na předpokladu, ne na ověřených datech.",
                "source": "assumption",
            }

        if source == "work_model":
            matched = self._matches_work_model(text)
            return {
                "verified": matched,
                "level": "verified" if matched else "unverified",
                "notes": (
                    "Tvrzení odpovídá schválenému WorkModelu."
                    if matched
                    else "Tvrzení se neshoduje s WorkModelem."
                ),
                "source": "work_model",
            }

        if source == "client_data":
            if evidence:
                return {
                    "verified": True,
                    "level": "verified",
                    "notes": "Tvrzení je podloženo daty klienta.",
                    "source": "client_data",
                }
            return {
                "verified": False,
                "level": "partial",
                "notes": "Zdroj je client_data, ale chybí konkrétní důkaz.",
                "source": "client_data",
            }

        if source == "face_model" or face_model_id is not None:
            return self.verify_against_face_model(text, face_model_id)

        return {
            "verified": False,
            "level": "unverified",
            "notes": "Neznámý zdroj tvrzení.",
            "source": source,
        }

    def verify_against_face_model(
        self,
        text: str,
        face_model_id: str | None = None,
    ) -> dict[str, Any]:
        """Ověří tvrzení proti konkrétnímu FaceModel vzoru nebo proti všem.

        Pokud face_model_id není uveden, hledá nejlepší shodu mezi všemi
        dostupnými FaceModel záznamy.
        """
        if not self.face_models:
            return {
                "verified": False,
                "level": "unverified",
                "notes": "K dispozici nejsou žádné FaceModel vzory.",
                "source": "face_model",
                "face_model_id": None,
            }

        text_lower = text.lower()
        best_match: dict[str, Any] | None = None
        best_score = 0.0

        for fm in self.face_models:
            fm_id = str(fm.get("model_id", fm.get("id", "")))
            if face_model_id is not None and fm_id != face_model_id:
                continue

            # Skóre shody: mechanism + applicable_to + tags
            mechanism = str(fm.get("mechanism", "")).lower()
            name = str(fm.get("name", "")).lower()
            tags = " ".join(fm.get("tags", [])).lower()
            applicable = " ".join(fm.get("applicable_to", [])).lower()

            searchable = f"{mechanism} {name} {tags} {applicable}"
            matches = sum(1 for w in text_lower.split() if w in searchable)
            score = matches / max(len(text_lower.split()), 1)

            if score > best_score:
                best_score = score
                best_match = {
                    "face_model_id": fm_id,
                    "name": fm.get("name", ""),
                    "mechanism": fm.get("mechanism", ""),
                    "score": score,
                }

        if best_match is None:
            return {
                "verified": False,
                "level": "unverified",
                "notes": "Tvrzení neodpovídá žádnému FaceModel vzoru.",
                "source": "face_model",
                "face_model_id": face_model_id,
            }

        if best_score >= 0.3:
            return {
                "verified": True,
                "level": "verified",
                "notes": (
                    f"Tvrzení odpovídá FaceModelu '{best_match['name']}' "
                    f"(mechanismus: {best_match['mechanism']})."
                ),
                "source": "face_model",
                "face_model_id": best_match["face_model_id"],
                "matched_mechanism": best_match["mechanism"],
                "confidence": round(best_score, 2),
            }

        return {
            "verified": False,
            "level": "partial",
            "notes": (
                f"Tvrzení částečně odpovídá FaceModelu '{best_match['name']}', "
                f"ale shoda je nízká (skóre {round(best_score, 2)})."
            ),
            "source": "face_model",
            "face_model_id": best_match["face_model_id"],
            "matched_mechanism": best_match["mechanism"],
            "confidence": round(best_score, 2),
        }

    def _matches_work_model(self, text: str) -> bool:
        """Jednoduchá kontrola shody s WorkModelem (keyword-based)."""
        if not self.work_model:
            return False
        text_lower = text.lower()
        processes = self.work_model.get("processes", [])
        for proc in processes:
            proc_name = str(proc.get("name", "")).lower()
            if proc_name and proc_name in text_lower:
                return True
        return False