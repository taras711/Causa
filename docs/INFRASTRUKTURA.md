# INFRASTRUKTURA.md – Strom infrastrukturních článků Causa

**Verze:** 1.0  
**Jazyk:** Čeština  
**Popis:** Detailní a jasný popis infrastrukturního uspořádání projektu Causa – hardwaru, softwaru, sítě, úložiště, bezpečnosti, nasazení a provozu. Strom je členěn do článků (kapitol), které spolu tvoří celkový infra obraz systému.

---

## 0. Přehledový strom infrastruktury

```
INFRASTRUKTURA (strom článků)
│
├── 1. Hardware (vývojový stroj a zákaznický server)
│   ├── 1.1 Vývojový stroj (lokální)
│   └── 1.2 Zákaznický server (produkční nasazení)
│
├── 2. Softwarová vrstva (runtime, runtime dependency)
│   ├── 2.1 Operační systém
│   ├── 2.2 Jazyk běhu a dependencies
│   ├── 2.3 LLM runtime (Ollama)
│   └── 2.4 Databázové servery
│
├── 3. Aplikační architektura (komunikace komponent)
│   ├── 3.1 Headless core služba (API + workflow engine)
│   ├── 3.2 Desktopová obal (UI + lokální core)
│   ├── 3.3 Serverová obal (stejné core, kontejnerizované)
│   └── 3.4 Komunikační schéma (synchronní vs. asynchronní)
│
├── 4. Úložiště dat (strom datových artikelů)
│   ├── 4.1 Relační databáze (SQLite / PostgreSQL)
│   ├── 4.2 Vektorové úložiště (pgvector / sqlite-vec)
│   ├── 4.3 Ledger (append-only auditní záznam)
│   ├── 4.4 Nahrané dokumenty (dočasné uploady)
│   └── 4.5 Zálohy a archivace
│
├── 5. Síť a komunikace
│   ├── 5.1 Lokální komunikace (desktop ↔ core ↔ Ollama)
│   ├── 5.2 Síťové rozhraní serveru (porty, firewall)
│   ├── 5.3 Reverse proxy (Nginx, SSL/TLS)
│   └── 5.4 Izolace tenantů (síťová a aplikační)
│
├── 6. Kontejnerizace a orchestrace
│   ├── 6.1 Docker obrazy (backend, UI, Ollama, PostgreSQL)
│   ├── 6.2 Docker Compose (lokální a produkční varianta)
│   └── 6.3 Volitelné IaC (Terraform / Ansible)
│
├── 7. Bezpečnost a řízení přístupu
│   ├── 7.1 Tenant isolation (oddělení klientů)
│   ├── 7.2 Šifrování (v klidu a v přenosu)
│   ├── 7.3 Auditní log (kdo, kdy, co)
│   ├── 7.4 Prompt injection obrana
│   └── 7.5 Tajemství (secrets management)
│
├── 8. Monitoring, telemetrie a logování
│   ├── 8.1 Metriky (latence, chybovost, využití GPU)
│   ├── 8.2 Logging (aplikační, systémové, auditní)
│   └── 8.3 Výstrahy a notifikace (volitelné, fáze 2+)
│
├── 9. Nasazení a aktualizace (deployment pipeline)
│   ├── 9.1 Vývojové nasazení (lokální)
│   ├── 9.2 Zákaznické nasazení (server u zákazníka)
│   └── 9.3 Aktualizace modelů a konfigurace
│
└── 10. Obnova po havárii a disaster recovery
    ├── 10.1 Zálohovací strategie (RPO, RTO)
    ├── 10.2 Obnovovací procedury
    └── 10.3 Testování obnovy
```

---

## 1. Hardware

### 1.1 Vývojový stroj (lokální)

| Komponenta | Specifikace | Poznámka |
|------------|-------------|----------|
| CPU | Ryzen 7 5800X (8 jader, 16 vláken) | Dostatečné pro celý MVP |
| GPU | RTX 5060 Ti 16 GB VRAM (původně uvedeno RTX 5600 Ti) | 16 GB VRAM je praktický strop pro modely třídy 14 B v Q4 kvantizaci (9–10 GB VRAM) |
| RAM | 32 GB | Dostatečné pro běh jednoho velkého modelu + malého embedding modelu vedle sebe |
| Úložiště | SSD (doporučeno NVMe) | Pro databázi, ledger, vektorové indexy |
| Síť | Lokální (bez nutnosti internetu pro běh modelů) | Ollama běží lokálně, žádná závislost na cloudu |

**Dopad na architekturu:**
- Jeden velký model najednou → agenti běží **sekvenčně**, paralelismus je výjimka.
- Praktický strop modelů: třída 14 B v Q4 kvantizaci s kontextem do ~16–32 tis. tokenů. Větší modely (24–32 B) buď těsně s malým kontextem, nebo přetečou do RAM a zpomalí.
- Dvojí běh s druhým modelem (diverzita u kritických kroků) znamená přepnutí modelu; s 32 GB RAM je přepnutí rychlé, ale počítá se s ním v rozpočtu času.
- Orientační doba případu: jednotky až nízké desítky minut (standardní režim), řádky minut (rychlý režim s 3 agenty).
- Čeština a španělština budou slabší než angličtina → EN jako kanonický jazyk.

### 1.2 Zákaznický server (produkční nasazení)

| Komponenta | Doporučená specifikace | Poznámka |
|------------|------------------------|----------|
| CPU | Stejný nebo výkonnější než vývojový stroj | Závisí na velikosti klienta a počtu souběžných případů |
| GPU | Volitelné; pokud k dispozici, 16+ GB VRAM | Pokud není GPU, běží modely v CPU režimu (pomalejší) |
| RAM | 32 GB+ | Více RAM umožňuje větší modely a rychlejší přepínání |
| Úložiště | SSD, pravidelné zálohy | Pro PostgreSQL, pgvector, ledger, zálohy |
| Síť | Lokální síť klienta, případně VPN pro vzdálený přístup | Nasazení je lokální (on-prem), není vyžadováno veřejné internetové připojení pro běh |

**Dopad:** Hardware zákazníka se bude lišit od vývojového stroje → **model je vždy konfigurace, nikdy předpoklad v kódu.** Konfigurace se předává přes `configs/prod.yaml` a proměnné prostředí.

---

## 2. Softwarová vrstva

### 2.1 Operační systém

- **Vývoj:** Windows 10/11 (prostředí vývojáře), WSL2 doporučeno pro Docker a Linuxové kontejnery.
- **Server (zákazník):** Linux (Ubuntu LTS nebo Debian stabilní), běží v Docker kontejnerech.
- **Proč:** Shodnost mezi vývojem a produkčním nasazením minimalizuje „funguje to jen na mém stroji“.

### 2.2 Jazyk běhu a dependencies

- **Python 3.11+** – pro backend, agenty, Quant Engine, workflow engine.
- **Node.js 18+** – pro webové UI (případně React/Vue + Vite).
- **Rust (volitelné)** – pro desktopovou obal Tauri (pokud se zvolí Tauri místo Electronu).
- **Správa dependencies:** `pyproject.toml` (Python), `package.json` (Node.js).

### 2.3 LLM runtime (Ollama)

- Ollama běží lokálně jako služba (desktop) nebo kontejner (server).
- Modely se stahují a spravují přes Ollama CLI/API.
- Podporované formáty: GGUF (kvantizace Q4, Q8).
- Model Router v aplikaci vybírá model podle typu kroku (malý pro klasifikaci, 14B pro uvažování).

### 2.4 Databázové servery

| Režim | Databáze | Vektorové rozšíření | Použití |
|-------|----------|---------------------|---------|
| Desktop | SQLite | sqlite-vec (nebo obdobné) | Lokální soubor, nulová instalace, snadná migrace |
| Server | PostgreSQL | pgvector | Tenant isolation, escala, ACID, vektorové vyhledávání |

Stejný datový model a migrace pro oba režimy (abstrakční vrstva nad úložištěm).

---

## 3. Aplikační architektura

### 3.1 Headless core služba

- API (FastAPI) – REST endpointy pro správu případů, agentů, znalostní báze, Quant Engine.
- Workflow engine s checkpointy – durable execution, obnova po restartu.
- Ledger – append-only záznam všech kroků, claimů a původů.
- Model Router – výběr a přepínání LLM modelů.

### 3.2 Desktopová obal

- Tenká aplikace kolem UI a lokálně spuštěného core.
- Uživatel pracuje v desktopové aplikaci, core běží na stejném stroji (lokálně).
- Žádná síťová závislost pro základní provoz (kromě prvního stažení modelů).

### 3.3 Serverová obal

- Stejné core jako desktop, zabalené v Docker kontejneru.
- Nasazeno na zákaznickém serveru (on-prem).
- Přístup přes webové UI nebo API (volitelně).

### 3.4 Komunikační schéma

```
Uživatel → UI (desktop/web) → API (FastAPI) → Workflow Engine → Agenti (sekvenčně)
                                               ↳ Ollama (LLM)
                                               ↳ Databáze (SQLite/PostgreSQL)
                                               ↳ Ledger (audit)
                                               ↳ Quant Engine (deterministické výpočty)
```

Komunikace mezi komponenty je primárně synchronní (HTTP / volání funkcí). Asynchronní fronta úloh se používá pro zpracování delších případů a pro retry mechanismy.

---

## 4. Úložiště dat (strom datových artikelů)

```
data/ (neversionováno, gitignored)
├── 4.1 Relační databáze
│   ├── SQLite: causa.db (jeden soubor, desktop)
│   └── PostgreSQL: databázový svazek (server, Docker volume)
│       ├── tabulky: cases, agents, claims, ledger, tenants, knowledge_records
│       └── indexy: full-text search, vektorové indexy (pgvector)
│
├── 4.2 Vektorové úložiště
│   ├── Embedding vektory pro FaceModel a WorkModel záznamy
│   ├── Hybridní retrieval: full-text + vektorové vyhledávání
│   └── TTL na záznamech (zastaralá conoscenza)
│
├── 4.3 Ledger (append-only auditní záznam)
│   ├── Každý claim, číslo a doporučení nese provenance
│   ├── Nezměnitelný zápis (pouze přidávání, žádné mazání)
│   ├── Viditelný v UI i v reportu
│   └── Základ pro verifikaci a důkaznost
│
├── 4.4 Nahrané dokumenty (dočasné uploady)
│   ├── Před zpracováním: dočasná složka
│   ├── Po zpracování: anonymizace a uložení extrakce (s odkazem na zdroj)
│   ├── Dokumenty vždy jako data, nikdy instrukce
│   └── Smazání po zpracování (neukládat surový text citlivých dokumentů)
│
└── 4.5 Zálohy a archivace
    ├── Šifrované zálohy databáze a ledgeru (denní, týdenní)
    ├── Úložiště záloh: lokální síťové úložiště nebo externí zašifrované médium
    └── Archivace starých případů podle TTL a politiky zákazníka
```

### Popis datových artikelů

| Článek | Popis | Umístění |
|--------|-------|----------|
| Relační databáze | Hlavní úložiště strukturovaných dat (případy, agenti, claimy, tenant) | `data/sqlite/` nebo `data/postgres/` |
| Vektorové úložiště | Semantické vyhledávání v znalostní bázi (FaceModel, WorkModel) | V rámci databáze (pgvector / sqlite-vec) |
| Ledger | Neměnný auditní záznam pro prokázání původu každého tvrzení | `data/ledger/` (souborové nebo v DB) |
| Nahrané dokumenty | Dočasné úložiště dokumentů klientů před anonymizací | `data/uploads/` (dočasné) |
| Zálohy | Šifrované kopie dat pro obnovu po havárii | `data/backups/` |


---

## 5. Síť a komunikace

### 5.1 Lokální komunikace (desktopový režim)

```
Uživatel (UI) ↔ localhost:PORT (FastAPI API)
FastAPI ↔ localhost:11434 (Ollama API)
FastAPI ↔ SQLite (lokální soubor)
```

Žádná externí síťová komunikace není vyžadována pro běh systému (kromě prvního stažení modelů přes Ollama).

### 5.2 Síťové rozhraní serveru (produkční)

| Služba | Port | Protokol | Poznámka |
|--------|------|----------|----------|
| FastAPI API | 8000 | HTTP / WebSocket | Hlavní rozhraní pro UI a externe klienty |
| Ollama | 11434 | HTTP | Lokální LLM runtime (pouze vnitřní) |
| PostgreSQL | 5432 | TCP | Pouze interní (nepřístupné zvenčí) |
| Nginx (reverse proxy) | 80, 443 | HTTP / HTTPS | Veřejné rozhraní, SSL termination |

Firewall: Povoleny pouze porty 80/443 (případně VPN). PostgreSQL a Ollama jsou přístupné pouze z vnitřní sítě kontejnerů.

### 5.3 Reverse proxy (Nginx)

- SSL/TLS termination (Let's Encrypt nebo interní certifikáty).
- Rate limiting (ochrana před přetížením).
- Směrování požadavků na backend (FastAPI) a statické soubory (UI).
- WebSocket podpora pro stav případu v reálném čase.

### 5.4 Izolace tenantů

- `tenant_id` je povinným sloupcem ve všech datových tabulkách od prvního dne.
- Dotazy jsou vždy filtrovány podle `tenant_id` (žádné křížové pronikání dat mezi klienty).
- Síťová izolace: každý tenant může mít vlastní instanci nebo sdílenou s tvrdou aplikační izolací.
- SSO, role a certifikace se odkládají do doby prvního korporátního zájemce (fáze po roce 1).

---

## 6. Kontejnerizace a orchestrace

### 6.1 Docker obrazy

| Obraz | Obsah | Base image |
|-------|-------|------------|
| `backend` | FastAPI, Python dependencies, core, agenty, Quant Engine | `python:3.11-slim` |
| `ui` | Webové UI (React/Vue + Vite build), statické soubory | `node:18-alpine` |
| `ollama` | Ollama binárka, předstažené modely (malý, 14B, embedding) | `ollama/ollama` |
| `postgres` | PostgreSQL + pgvector | `postgres:15` s pgvector rozšířením |

### 6.2 Docker Compose

- `docker-compose.yml` – lokální vývojové nasazení (backend + UI + Ollama + PostgreSQL).
- `docker-compose.prod.yml` – produkční varianta (s pgvector, zálohami, monitoringem, omezenými zdroji).

Spuštění: `docker-compose up -d` (lokálně) nebo `docker-compose -f docker-compose.prod.yml up -d` (produkce).

### 6.3 Volitelné IaC (Infrastructure as Code)

Pro zákaznické servery se mohou použít Terraform nebo Ansible pro:
- Zřizování virtuálních strojů.
- Instalaci Dockeru a docker-compose.
- Konfiguraci firewallu a sítě.
- Spuštění kontejnerů s Causa.

Tato vrstva je volitelná a může být přidána v fázi 2+ nebo při prvním korporátním zákazníkovi.

---

## 7. Bezpečnost a řízení přístupu

### 7.1 Tenant isolation

- Každý tenant má izolovaná data (databázové řady s `tenant_id`).
- Žádné sdílení claimů, případů ani znalostí mezi tenanty bez explicitního souhlasu.
- Auditní log zaznamenává přístup podle tenantu.

### 7.2 Šifrování

| Co se šifruje | Kde | Jak |
|---------------|-----|-----|
| Data v klidu | Databázové soubory, ledger, zálohy | Šifrování na úrovni úložiště (LUKS, BitLocker) nebo šifrované zálohy |
| Data v přenosu | Síť (API, UI, databáze) | TLS 1.2+ (Nginx reverse proxy, interní TLS mezi kontejnery) |
| Citlivá pole | Hesla, API klíče, citlivá data klientů | Šifrování na úrovni aplikace (AES-256) |

### 7.3 Auditní log

- Kdo, kdy, co provedl (vytvoření případu, spuštěí agenta, změna konfigurace, přístup k datům).
- Ukládáno v ledgeru (append-only, nelze měnit).
- Viditelné v UI pro správce a v reportech.

### 7.4 Prompt injection obrana

- Dokumenty nahrané uživatelem jsou vždy **data**, nikdy instrukce.
- Agenti pracující s dokumenty nemají nástroje s vedlejšími efekty (žádné odesílání e-mailů, žádné úpravy databáze).
- Filtrace a označování nedůvěryhodných vstupů.
- Oddělené kontexty pro důvěryhodné a nedůvěryhodné zdroje.

### 7.5 Tajemství (secrets)

- Hesla k databázím, API klíče, šifrovací klíče jsou v proměnných prostředí (`.env`), nikdy v kódu.
- `.env.example` je verzován jako šablona; reálné `.env` je v `.gitignore`.
- V produkci lze použít Docker secrets nebo 외부 secret manager (HashiCorp Vault, AWS Secrets Manager atd.).


---

## 8. Monitoring, telemetrie a logování

### 8.1 Metriky

| Metrika | Zdroj | Účel |
|---------|-------|------|
| Latence odpovědi modelu | Ollama / aplikace | Detekce pomalých modelů, optimalizace |
| Chybovost API (5xx) | FastAPI | Detekce výpadků, chyb v kódu |
| Využití GPU a VRAM | Ollama / nvidia-smi | Ochrana před vyčerpáním paměti |
| Počet kroků případu | Workflow engine | Detekce explozivních smyček, optimalizace pipeline |
| Doba zpracování případu | Workflow engine | SLA pro zákazníka, odhad nákladů |

### 8.2 Logging

- Aplikační logy (Python `logging`, JSON formát pro snadné parsování).
- Systémové logy (Docker, Ollama, Nginx).
- Auditní logy (ledger, přístupy k datům).
- Úrovně: DEBUG (vývoj), INFO (provoz), WARNING, ERROR, CRITICAL.

### 8.3 Výstrahy a notifikace

- Volitelné, fáze 2+ (Prometheus + Grafana, e-mail/Slack notifikace).
- Výstrahy: pád Ollamy, vyčerpání GPU, vysoká chybovost, neúspěšný případ.

---

## 9. Nasazení a aktualizace

### 9.1 Vývojové nasazení (lokální)

```bash
# Klon repozitáře
git clone <repo> causa
cd causa

# Konfigurace
cp .env.example .env
# Upravit .env pro lokální prostředí

# Spuštěí
docker-compose up -d
```

### 9.2 Zákaznické nasazení (server u zákazníka)

1. Připravit server s Linuxem, Dockerem a docker-compose.
2. Zkopírovat `docker-compose.prod.yml`, `configs/prod.yaml`, `.env.example`.
3. Upravit konfiguraci pro zákazníka (tenant_id, hesla, cesty k modelům).
4. Spustit: `docker-compose -f docker-compose.prod.yml up -d`.
5. Ověřit funkčnost přes webové UI nebo API.
6. Pravidelné zálohy databáze a ledgeru.

**Důležité:** Model je vždy konfigurace, nikdy předpoklad v kódu. Pokud zákazník má jiný hardware, změna se provede v `models.yaml`, nikoli v zdrojovém kódu.

### 9.3 Aktualizace modelů a konfigurace

- Nové modely se stáhnou přes Ollama (`ollama pull <model>`).
- Konfigurace modelů se aktualizuje v `models.yaml` nebo přes proměnné prostředí.
- Aktualizace aplikace: nový Docker obraz, `docker-compose pull && docker-compose up -d`.
- Migrace databáze se spustí automaticky při startu (`scripts/migrate.py`).

---

## 10. Obnova po havárii a disaster recovery

### 10.1 Zálohovací strategie

| Co se zálohuje | Frekvence | Umístění | Šifrování |
|----------------|-----------|----------|-----------|
| Relační databáze | Denní (inkrementální), týdenní (plná) | `data/backups/` | Ano (AES-256) |
| Ledger | Denní | `data/backups/` | Ano |
| Vektorové indexy | Týdenní | `data/backups/` | Ano |
| Konfigurace (`configs/`) | Při změně | Verzováno v Gitu | Ne (neobsahuje citlivá data) |

**RPO (Recovery Point Objective):** Maximálně 24 hodin ztracených dat (denní záloha).  
**RTO (Recovery Time Objective):** Obnovení do 4 hodin od selhání.

### 10.2 Obnovovací procedury

1. Nainstalovat čistý server s Dockerem.
2. Obnovit databázi a ledger ze šifrované zálohy.
3. Spustit `docker-compose.prod.yml`.
4. Ověřit integritu dat (počet případů, claimů, tenantů).
5. Ověřit funkčnost přes API/UI.

### 10.3 Testování obnovy

- Test obnovy se provádí minimálně jednou za čtvrtletí (fáze 2+).
- Výsledek testu se zaznamenává do provozní dokumentace.
- V případě selhání testu se aktualizují záložní skripty a procedury.

---

## 11. Souvislosti s dalšími dokumenty

| Dokument | Vztah k INFRASTRUKTURA.md |
|----------|---------------------------|
| `BaseModel – strategický plán a revidovaná architektura.md` | Zdrojový strategický plán; hardware a roadmapa vycházejí z kapitoly 18.10. |
| `TECHNICKA_DOKUMENTACE.md` | Technické kroky implementace; infra dokumentace je provozní vrstva nad nimi. |
| `Structure.md` | Popisuje kde v repozitáři najdete konfigurační a infra soubory (`infrastructure/`, `configs/`, `data/`). |

---

## 12. Seznam rozhodnutí (ADR – volitelné)

Budoucí rozhodnutí o infrastrukturních změnách (např. přechod z Ollama na vLLM, přidání multi-tenantu, změna databáze) se budou zapisovat do `docs/adr/` ve formátu Architectural Decision Records.

