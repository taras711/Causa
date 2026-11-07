# Structure.md – Projektová struktura Causa

**Verze:** 1.0  
**Jazyk:** Čeština  
**Popis:** Jasaná popisná struktura celého projektu se základem v adresáři `Causa/`. Každý adresář a důležitý soubor má přiřazen popis svého účelu.

---

## 1. Kořen projektu

```
c:\Users\taras\OneDrive\Desktop\Projects\Apps\Causa\
├── docs/                  # Veškerá dokumentace (strategická, technická, infrastrukturní)
├── src/                   # Zdrojový kód aplikace (core, API, agenti, UI)
├── tests/                 # Automatické testy (unit, integrační, evaluační)
├── configs/               # Konfigurační soubory (modely, pipeline, tenants)
├── infrastructure/        # Definice infrastruktury (Docker, docker-compose, IaC)
├── data/                  # Lokální data (SQLite, vektory, ledger, zálohy) – gitignored
├── scripts/               # Pomocné skripty (build, deploy, ingestion, anonymizace)
├── .gitignore             # Vyloučené soubory z verzování
├── .env.example           # Příklad proměnných prostředí (necommitovat reálné hodnoty)
├── README.md              # Úvodní stránka projektu, návod ke spuštění
├── LICENSE                # Licence projektu
└── pyproject.toml         # Python projektová konfigurace, dependencies, build systém
```

### Popis kořenových adresářů

| Adresář | Účel |
|---------|------|
| `docs/` | Strategický plán, technická dokumentace, popis struktury, infrastrukturní dokumentace, rozhodnutí (ADR). |
| `src/` | Zdrojový kód: backend API, workflow engine, agenci, Quant Engine, UI (desktop/web), sdílené knihovny. |
| `tests/` | Testy rozdělené podle typu: unit, integrační, evaluační (zlaté případy), bezpečnostní. |
| `configs/` | Konfigurace pro olika prostředí (dev, prod), modelové konfigurace, tenant konfigurace, proměnné prostředí. |
| `infrastructure/` | Dockerfiles, docker-compose, Terraform/Ansible (volitelné), definición sítí, svazků, tajných klíčů. |
| `data/` | Lokální úložiště databází, vektorových indexů, ledgeru a záloh. V gitovém repozitáři není verzeováno. |
| `scripts/` | Skripty pro spuštění, build, deploy, ingestion dat, anonymizaci, migrace databáze. |

---

## 2. Adresář `src/` – Zdrojový kód

```
src/
├── core/                  # Headless core služba (workflow engine, ledger, orchestrátor)
│   ├── __init__.py
│   ├── engine.py          # Workflow engine s checkpointy a durable execution
│   ├── ledger.py          # Neměnný záznam kroků, claimů a původů (provenance)
│   ├── case.py            # Model případu (Case), stav, životní cyklus
│   └── router.py          # Model Router (výběr a přepínání LLM modelů)
├── api/                   # FastAPI rozhraní (REST endpoints, WebSocket pro stav případu)
│   ├── __init__.py
│   ├── main.py            # Vstupní bod API, inicializace aplikace
│   ├── routes/            # Endpointy rozdělené podle domény
│   │   ├── cases.py       # Správa případů (vytvoření, stav, výsledek)
│   │   ├── agents.py      # Spuštěí agentů, seznam agentů
│   │   ├── knowledge.py   # Kvalostní báze, FaceModel, retrieval
│   │   └── quant.py       # Quant Engine (ROI, citlivost, simulace)
│   ├── dependencies.py    # Dependency injection (databáze, konfigurace, auth)
│   └── middleware.py      # Middleware (logging, CORS, auditní log)
├── agents/                # Typované agenty (funkce se vstupním/výstupním schématem)
│   ├── __init__.py
│   ├── base.py            # Základní třída agenta (schéma, úroveň autonomie L0–L3)
│   ├── framer.py          # Framer – definuje rozsah případu a strukturu A3
│   ├── diagnostician.py   # Diagnostician – A3 logika, analýza příčin
│   ├── evidence_retriever.py  # Evidence Retriever – vyhledávání v znalostní bázi
│   ├── solution_designer.py   # Solution Designer – návrh řešení + kvantifikace
│   ├── red_team.py        # Red Team – oponentura, argumentace PRO/PROTI
│   └── synthesizer.py     # Synthesizer – shrnutí, finální report
├── knowledge/             # Znalostní vrstva (FaceModel, WorkModel, retrieval)
│   ├── __init__.py
│   ├── schema.py          # Schéma FaceModelu a WorkModelu
│   ├── ingestion.py       # Ingestion pipeline (anonymizace, extrakce, kurace)
│   ├── retrieval.py       # Hybridní retrieval (full-text + vektorové vyhledávání)
│   ├── verification.py    # Verifikační vrstva (ověření claimu proti zdroji)
│   └── curation.py        # Kurační fronty, schvalování záznamů
├── quant/                 # Deterministické výpočetní jádro (ne LLM)
│   ├── __init__.py
│   ├── engine.py          # Quant Engine (ROI, návratnost, citlivost)
│   ├── monte_carlo.py     # Základní simulace Monte Carlo
│   ├── assumptions.py     # Graf předpokladů s přepočtem dotčených větví
│   └── models.py          # Datové modely pro kvantifikaci (Pydantic)
├── ui/                    # Uživatelské rozhraní (desktop nebo web)
│   ├── desktop/           # Desktopová obal (Tauri / Electron + webview)
│   └── web/               # Webové UI (React / Vue + Vite)
├── shared/                # Sdílené knihovny a utility
│   ├── __init__.py
│   ├── schemas.py         # Sdílené Pydantic schémata (vstupy/výstupy kroků)
│   ├── utils.py           # Pomocné funkce (datum, hash, šifrování)
│   ├── security.py        # Bezpečnostní helpery (tenant isolation, audit, filtrace)
│   └── i18n.py            # Internacionalizace (texty mimo kód, EN → CS → ES)
└── config.py              # Načítání konfigurace z proměnných prostředí a souborů
```

### Popis klíčových komponent `src/`

| Komponenta | Popis |
|------------|-------|
| `core/engine.py` | Workflow engine s checkpointy; po pádu systému případ pokračuje od posledního bodu. |
| `core/ledger.py` | Nezměnitelný záznam (append-only log) všech claimů, čísel a jejich původu pro audit. |
| `agents/base.py` | Abstraktní rozhraní agenta: vstupní schéma, výstupní schéma, úroveň autonomie (L0–L3). |
| `knowledge/ingestion.py` | Načítání externích zdrojů s povinnou anonymizací dat klienta před uložením. |
| `quant/engine.py` | Deterministické výpočty (ROI, citlivost); LLM sem nikdy nezasílá surová čísla k vygenerování. |
| `api/routes/cases.py` | Endpointy pro správu životního cyklu případu (intake → report). |


---

## 3. Adresář `tests/` – Automatické testy

```
tests/
├── __init__.py
├── conftest.py            # Shared pytest fixtures (databáze, mock Ollama, testovací klient)
├── unit/                  # Unit testy jednotlivých modulů
│   ├── test_ledger.py
│   ├── test_engine.py
│   ├── test_quant.py
│   └── test_schemas.py
├── integration/           # Integrační testy (API → DB → agenti)
│   ├── test_case_flow.py
│   ├── test_agent_chain.py
│   └── test_ingestion.py
├── eval/                  # Evaluační sada (zlaté případy, ablační testy, regrese)
│   ├── golden_cases/      # Anonymizované zlaté A3 případy (test data)
│   ├── test_regression.py # Regresní testy po změně promptu/modelu
│   └── test_ablation.py   # Ablační testy (řetěz vs. singolo prompt)
└── security/              # Bezpečnostní testy (prompt injection, tenant isolation)
    ├── test_injection.py
    └── test_isolation.py
```

| Podadresář | Účel |
|------------|------|
| `unit/` | Testy izolovaných funkcí a tříd bez externích závislostí. |
| `integration/` | Testy propojení modulů (API volá engine, engine zapisuje do ledgeru). |
| `eval/` | Evaluační harness se zlatými případy; spouští se v CI při každé změně. |
| `security/` | Testy odolnosti proti útokům (prompt injection, únik dat mezi tenanty). |

---

## 4. Adresář `configs/` – Konfigurace

```
configs/
├── dev.yaml               # Konfigurace pro vývojové prostředí (lokální Ollama, SQLite)
├── prod.yaml              # Konfigurace pro produkční/serverové nasazení (PostgreSQL, Docker)
├── models.yaml            # Konfigurace modelů (malý, 14B, embedding, teplota, max tokeny)
├── tenants/               # Konfigurace jednotlivých tenantů (klientů)
│   └── example_tenant.yaml
└── logging.yaml           # Konfigurace logování (úroveň, formát, výstup)
```

| Soubor | Účel |
|--------|------|
| `dev.yaml` | Rychlé lokální nastavení pro vývojáře (malé modely, malý kontext, lokální databáze). |
| `prod.yaml` | Serverové nastavení pro zákazníka (PostgreSQL, tenant isolation, auditní log). |
| `models.yaml` | Výběr modelů přes Model Router; model je konfigurace, nikdy hardcodovaný předpoklad. |
| `tenants/` | Izolace klientů: každý tenant má vlastní konfiguraci a oddělená data. |

---

## 5. Adresář `infrastructure/` – Definice infrastruktury

```
infrastructure/
├── docker/
│   ├── Dockerfile.backend     # Obraz pro headless core službu (FastAPI + Python)
│   ├── Dockerfile.ui          # Obraz pro webové UI (Node.js + Vite build)
│   └── Dockerfile.ollama      # Obraz s Ollama a nataženými modely
├── docker-compose.yml         # Lokální orchestrace (backend + UI + Ollama + PostgreSQL)
├── docker-compose.prod.yml    # Produkční varianta (s pgvector, zálohami, monitoringem)
├── nginx/
│   └── nginx.conf             # Reverse proxy, SSL termination, rate limiting
├── monitoring/
│   ├── prometheus.yml         # Sběr metrií (latence, chybovost, využití GPU)
│   └── grafana/               # Dashboards pro provozní telemetrii
├── backups/
│   └── backup_script.sh       # Skript pro šifrované zálohování databází a ledgeru
└── iac/                       # Volitelné: Terraform / Ansible pro zákaznické servery
    ├── main.tf
    └── variables.tf
```

Podrobný popis infrastrukturního stromu je v samostatném dokumentu `INFRASTRUKTURA.md`.

---

## 6. Adresář `data/` – Lokální data (gitignored)

```
data/
├── sqlite/                    # SQLite databáze pro desktopový režim
│   └── causa.db
├── postgres/                  # Datová složka PostgreSQL (pouze v kontejnerech)
├── vectors/                   # Vektorové indexy (pgvector / sqlite-vec)
├── ledger/                    # Append-only ledger soubory (auditní záznamy)
├── backups/                   # Šifrované zálohy (denní, týdenní)
└── uploads/                   # Nahrané dokumenty klientů (dočasné, před anonymizací)
```

> Pozor: adresář `data/` je v `.gitignore` a není verzován. Obsahuje citlivá data klientů.

---

## 7. Adresář `scripts/` – Pomocné skripty

```
scripts/
├── run_dev.sh                 # Spuštění vývojového prostředí
├── build.sh                   # Sestavení Docker obrazů
├── deploy.sh                  # Nasazení na zákaznický server
├── ingest.py                  # Spuštěí ingestion pipeline (znalostní báze)
├── anonymize.py               # Anonymizace dat klienta před uložením
├── migrate.py                 # Migrace databázového schématu
└── backup.sh                  # Spuštěí zálohování
```

---

## 8. Konfigurační soubory v kořenu

| Soubor | Popis |
|--------|-------|
| `.gitignore` | Vyloučené adresáře a soubory (`data/`, `__pycache__`, `.env`, `*.log`, `node_modules/` atd.). |
| `.env.example` | Šablona proměnných prostředí (DB hesla, API klíče, cesty k modelům). Reálné hodnoty se necommitují. |
| `README.md` | Úvod do projektu, návod ke spuštění, architektura v kostce, odkazy na dokumentaci. |
| `LICENSE` | Licence pod jakou je projekt versprezován. |
| `pyproject.toml` | Python projekt: dependencies (FastAPI, SQLAlchemy, pgvector, Ollama klient, pytest atd.), build systém. |

---

## 9. Pravidla udržování struktury

1. **Žádný kód mimo `src/`**: Veškerá aplikační logika žije v `src/`. Skripty v `scripts/` jsou jen spouštěcí a utility.
2. **Konfigurace mimo kód**: Veškerá nastavení (modely, tenant_id, cesty) v `configs/` nebo proměnných prostředí, nikdy hardcodováno.
3. **Data mimo git**: `data/` je gitignored; citlivá data klientů nikdy do verzování.
4. **Dokumentace v `docs/`**: Veškerá dokumentace (strategická, technická, struktura, infrastruktura) je v `docs/`.
5. **Testy vedle kódu**: Každá nová funkce v `src/` má odpovídající test v `tests/`.

