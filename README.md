# Causa – lokální, auditovatelná platforma pro firemní rozhodování

Causa produkuje strukturovanou analýzu opřenou o ověřené vzory (WorkModel / FaceModel)
místo „odpovědi chatbota“. Každé tvrzení, číslo a doporučení musí být dohledatelné:
buď na důkaz ve WorkModelu, na data klienta, nebo na explicitně označený předpoklad.

## Architektura v kostce

- **Headless core** (FastAPI + workflow engine + ledger) – identique pro desktop i server
- **Agenti jako typované funkce** (Pydantic schéma vstupu/výstupu, vlastní nástroje, úroveň autonomy L0–L3)
- **Deterministické výpočetní jádro** – LLM nikdy nevyrábí čísla, jen navrhuje strukturu a vysvětluje
- **Durable execution** – checkpointy po každém kroku, obnova po restartu
- **Lokální LLM přes Ollama** – modely jako konfigurace, nikdy hardcodováno

## Struktura repozitáře

```
docs/          # Strategická, technická a infrastrukturní dokumentace
src/           # Zdrojový kód (core, API, agenti, modely, knowledge, quant, UI)
tests/         # Unit, integrační, evaluační a bezpečnostní testy
configs/       # Konfigurace (modely, pipeline, tenants, prostředí)
infrastructure/# Docker, docker-compose, nginx, monitoring, IaC
data/          # Lokální data (SQLite, vektory, ledger, zálohy) – gitignored
scripts/       # Pomocné skripty (spuštění, build, deploy, ingestion, migrace)
```

## Rychlý start (vývoj)

```bash
# 1. Naklonuj / otevřít repozitář
cd causa

# 2. Vytvoř virtuální prostředí a nainstaluj závislosti
python -m venv .venv
.venv\Scripts\activate        # Windows
# nebo: source .venv/bin/activate  # Linux/macOS

pip install -e .

# 3. Připrav konfiguraci
cp .env.example .env
# Uprav .env podle svého prostředí

# 4. Spusť Ollama a stáhněte modely
ollama pull qwen3.5:4b
ollama pull qwen3:14b
ollama pull hf.co/Qwen/Qwen3-14B-GGUF:Q5_K_M
ollama pull nomic-embed-text

# 5. Spusť aplikaci
python -m src.api.main

# Nebo přes Docker Compose
docker-compose -f infrastructure/docker-compose.yml up -d
```

## Roadmapa (12 měsíců, jeden vývojář)

1. **Měsíc 1 – validace:** zlaté A3 případy, prototyp řetězu promptů, ablace, test lokálních modelů (EN/CS)
2. **Měsíce 2–3 – walking skeleton:** core služba, workflow s checkpointy, ledger, kontrakty agentů, 3 agenti, evaluační harness
3. **Měsíce 4–6 – znalostní jádro:** schéma FaceModelu, A3 ingestion, 30–50 kurátorovaných záznamů, hybridní retrieval, verifikační vrstva
4. **Měsíce 7–8 – kvantifikace a Red Team:** Quant Engine (ROI, citlivost, Monte Carlo), graf předpokladů
5. **Měsíce 9–10 – automatizace a zpevnění:** kurační fronty, učící smyčka, telemetrie, zálohy, bezpečnost
6. **Měsíce 11–12 – pilot a rezerva:** pilot s design partnerem, rezerva 20–25 % času

## Testování

Projekt obsahuje evaluační harness se unit a evaluačními testy:

```bash
# Spustit všechny testy
python -m pytest tests/ -v

# Pouze unit testy
python -m pytest tests/unit/ -v -m unit

# Pouze evaluační testy (zlaté A3 případy)
python -m pytest tests/eval/ -v -m eval

# Testy s pokrytím kódu (vyžaduje pytest-cov)
python -m pytest tests/ --cov=src --cov-report=html
```

Testy jsou rozděleny do podsložek:
- `tests/unit/` – unit testy (Case model, Ledger, WorkflowEngine, Settings, schémata agentů, mocknuté agenty)
- `tests/eval/` – evaluační testy se zlatými A3 případy (conftest + test_golden_a3)
- `tests/integration/` – připraveno pro integrační testy
- `tests/security/` – připraveno pro bezpečnostní testy

Markery pytest: `unit`, `integration`, `eval`, `security`.

## Dokumentace

- `docs/BaseModel – strategický plán a revidovaná architektura.md` – strategický plán
- `docs/TECHNICKA_DOKUMENTACE.md` – technická dokumentace a návrh implementace
- `docs/Structure.md` – popis adresářové struktury
- `docs/INFRASTRUKTURA.md` – infrastrukturní uspořádání

## Licence

Viz `LICENSE`.