# Technická dokumentace – Causa (A3 problem-solving engine)

**Verze:** 1.0  
**Zdroj:** `docs/BaseModel – strategický plán a revidovaná architektura.md`  
**Jazyk:** Čeština  
**Stav:** Počáteční návrh k realizaci

---

## 1. Účel a rozsah

Tento dokument překládá strategický plán do konkrétních technických kroků, návrhů architektury, rizik a jejich dopadů. Slouží jako hlavní technický podklad pro implementaci a pro rozhodování o priorizaci práce jednoho vývojáře v rámci 12měsíční roadmapy.

Cílový stav: lokální, auditovatelná platforma pro firemní rozhodování, která produkuje strukturovanou analýzu opřenou o ověřené vzory (WorkModel / FaceModel) místo „odpovědi chatbota“. Každé tvrzení, číslo a doporučení musí být dohledatelné na důkaz v WorkModelu, na data klienta nebo na explicitně označený předpoklad.

---

## 2. Technologický stack (návrh)

Níže uvedený stack vychází z hardwarových limitů vývojového stroje (Ryzen 7 5800X, GPU 16 GB VRAM, 32 GB RAM) a z požadavku na lokální běh.

| Vrstva | Návrh | Odůvodnění |
|--------|-------|------------|
| Jazyk běhu | Python 3.11+ | Nejširší podpora pro LLM/ML knihovny, snadná integrace s Ollama |
| API / backend | FastAPI | Rychlý vývoj, automatická dokumentace, async podpora |
| Workflow engine | Temporal (pokud hardware umožní) nebo vlastní lehký engine s checkpointy (SQLite) | Durable execution, checkpointy za krok, obnova po restartu |
| Databáze (desktop) | SQLite + vektorové rozšíření | Nulová instalace, lokální soubor, snadná migrace na PostgreSQL |
| Databáze (server) | PostgreSQL + pgvector | Tenant isolation, escala, ACID, vektorové vyhledávání |
| Vektorové uložiště | pgvector / sqlite-vec | Hybridní retrieval (klíčová slova + sémantika) |
| LLM runtime | Ollama (lokální) | Modelové přepínání, Q4 kvantizace, 14B strop na 16 GB VRAM |
| Modelové třídy | Malý 4–8 B (klasifikace, extrakce), 14 B (úvaha, syntéza), embedding 1–2 GB | Vejde se do VRAM vedle sebe, sekvenční běh agentů |
| Strukturovaný výstup | JSON Schema (Ollama native) + Pydantic | Validace schématu, automatická oprava chybného výstupu |
| Frontend (desktop) | Tauri (Rust + webview) nebo Electron | Lokální desktopová aplikace nad headless core |
| Frontend (web/server) | React nebo Vue + Vite | Stejné jádro, jiný obal (viz kapitola 18.3 strategického plánu) |
| Testování | pytest, hypothesis, evaluační harness | Regresní evaluace po změně promptu/modelu |
| CI/CD | GitHub Actions | Automatické testy, build artefaktů, security scan |
| Kontejnerizace | Docker + docker-compose | Snadné nasazení na zákaznický server |
| Monitoring | Prometheus + Grafana (volitelné, fáze 2) | Provozní telemetrie, latence, chybovost |
| Zálohování | Restic / kopia (zašifrované) | Šifrované zálohy lokálních databází a ledgeru |


---

## 3. Architektonické návrhy

### 3.1 Princip „jedno jádro, dva obaly“

Core je headless služba (API, workflow engine, znalostní vrstva). Desktop aplikace je tenký obal kolem UI a lokálně spuštěného core. Serverová verze je stejné core v kontejneru. Datový model a migrace jsou sdílené.

### 3.2 Agenti jako typované funkce

Agenti nejsou „osobnosti“, ale typované funkce s:
- Vstupním a výstupním schématem (Pydantic modely)
- Vlastními nástroji (pouze čtení, žádné vedlejší efekty pro nedůvěryhodné dokumenty)
- Vlastním rozsahem znalostí
- Určenou úrovní autonomie (L0–L3)

MVP agenti (4–5 funkcí):
1. **Framer** – definuje rozsah případu a strukturu A3
2. **Diagnostician** – A3 logika, analýza příčin
3. **Evidence Retriever** – vyhledávání v znalostní bázi a datech klienta
4. **Solution Designer** – návrh řešení s kvantifikací (Quant Engine)
5. **Red Team + Synthesizer** – oponentura, shrnutí, finální report

### 3.3 Deterministické výpočetní jádro (Quant Engine)

LLM nikdy nevyrábí čísla. LLM smí navrhnout strukturu modelu a vysvětlit výsledek, ale čísla (ROI, citlivost, kapacita, cashflow) počítá deterministické jádro s parametry z dat klienta nebo z označených předpokladů.

### 3.4 Důkazní vrstva (ledger)

Každé tvrzení, číslo a doporučení nese metadata původu (provenance):
- Odkaz na WorkModel / FaceModel
- Odkaz na data klienta
- Explicitní označení předpokladu
- Úroveň důvěry (složené skóre z kvality zdrojů, počtu nezávislých zdrojů, shody napříč běhy, úplnosti dat, výsledku verifikace)

Neověřitelné claimy nesmí vstoupit do doporučení. Stav `unverified` je viditelný v UI i v reportu.

---

## 4. Technické kroky implementace (fázový plán)

Kroky vycházejí z 12měsíční roadmapy pro jednoho vývojáře (kapitola 18.8 strategického plánu). Každá fáze obsahuje konkrétní dodávky, akzeptační kritéria a rizika.

### Fáze 0 – Příprava a validace (Měsíc 1)

**Cíl:** Ověřit, že základní myšlenka funguje na lokálním hardware a že jeden promptový řetězec přináší hodnotu nad singolo promptem.

**Technické kroky:**
1. Nastavit vývojové prostředí (Python, Ollama, Git, GitHub repository, CI).
2. Vybrat a otestovat kandidáty modelů v Ollamě (malý 4–8 B, 14 B třída, embedding model).
3. Vytvořit prototyp řetězu promptů (Framer → Diagnostician → Synthesizer) bez workflow enginu.
4. Definovat zlaté A3 případy (anonymizované, manuálně označené správné řešení).
5. Spustit ablační test: řetěz promptů vs. singolo prompt na zlatých případech.
6. Otestovat lokální modely v EN a CS.
7. Vytvořit základní evaluační harness (sada testů, porovnání výstupu se zlatým standardem).

**Dodávky:** Funkční prototyp, sada zlatých případů, evaluační harness, zpráva o vhodnosti modelů.

**Rizika:** Lokální model nedosáhne požadované kvality v češtině; hardware nestíhá paralelní běh.  
**Dopad:** Pokud selže, tilbage na EN jako kanonický jazyk, čeština jako lokalizovaný pohled (viz strategický plán 18.5).

### Fáze 1 – Walking skeleton (Měsíce 2–3)

**Cíl:** Minimální funkční systém s core službou, workflow enginem, ledgerem, kontrakty agentů a 3 agenty.

**Technické kroky:**
1. Implementovat headless core službu v FastAPI.
2. Implementovat workflow engine s checkpointy (perzistentní stav případu, obnova po restartu).
3. Vytvořit datový model (SQLite pro desktop, připraveno na PostgreSQL) s `tenant_id` od začátku.
4. Implementovat ledger – nezměnitelný záznam všech kroků, claimů a původů.
5. Definovat Pydantic kontrakty mezi kroky (typované vstupy/výstupy).
6. Implementovat 3 agenty: Framer, Diagnostician, Evidence Retriever.
7. Implementovat validaci schémat na výstupech modelů (JSON Schema + automatická oprava retry).
8. Spustit evaluační harness v CI (regresní testy při každé změně).

**Dodávky:** Walking skeleton, 3 agenti, ledger, schéma databáze, evaluační harness v CI.

**Rizika:** Chybný výstup modelu propustí validací; kaskádová chyba mezi kroky.  
**Dopad:** Použití circuit breakeru, fallback na menší model, označení mezery v reportu.


### Fáze 2 – Znalostní jádro (Měsíce 4–6)

**Cíl:** Schéma FaceModelu, ingestion A3 případů s anonymizací, hybridní retrieval, verifikační vrstva, 30–50 kurátorovaných záznamů.

**Technické kroky:**
1. Navrhnout schéma FaceModelu (kontext, mechanismus úspěchu, podmínky použití, původ, TTL).
2. Implementovat ingestion pipeline s povinnou anonymizací dat klienta.
3. Implementovat hybridní retrieval (full-text + vektorové vyhledávání).
4. Implementovat verifikační vrstvu (ověření claimu proti zdroji, stav `unverified`/`verified`).
5. Naimportovat a kurátovat 30–50 kvalitních záznamů (veřejně známé, licenčně čisté zdroje).
6. Implementovat terminologický slovník lean pojmů (kaizen, muda, A3).
7. Přidat multi-language embeddings (EN canonical, CS lokalizace).

**Dodávky:** FaceModel schéma, ingestion pipeline, retrieval, verifikace, 30–50 záznamů.

**Rizika:** Právní riziko kopírování textů; nedostatek kvalitních zdrojů; cold-start znalostní báze.  
**Dopad:** Ukládat vlastní strukturovanou extrakci s odkazem na zdroj, ověřit licence před komerčním použitím, kurátorem je na začátku vývojář.

### Fáze 3 – Kvantifikace a Red Team (Měsíce 7–8)

**Cíl:** Minimální Quant Engine (ROI, citlivost, základní Monte Carlo), graf předpokladů s přepočtem dotčených větví, Red Team agent.

**Technické kroky:**
1. Implementovat deterministický Quant Engine (rozdělený od LLM).
2. Implementovat graf předpokladů s automatickým přepočtem dotčených větví při změně parametru.
3. Implementovat základní simulaci (citlivostní analýza, Monte Carlo pro nejisté vstupy).
4. Implementovat Red Team agenta (oponent, hledání slabin v řešení, argumentace PRO/PROTI).
5. Propojit Solution Designer s Quant Engineem (čísla z jádra, ne od LLM).
6. Přidat brány pro člověka (nízká úplnost dat, rozpor mezi agenty, P1 doporučení bez evidence stupně B+).

**Dodávky:** Quant Engine, graf předpokladů, Red Team, brány pro člověka.

**Rizika:** LLM vymýšlí čísla (falešná přesnost); špatně kalibrované sebehodnocení jistoty.  
**Dopad:** Vynutit deterministické výpočty, složené skóre důvěry, kalibrace podle skutečných výsledků.

### Fáze 4 – Automatizace a zpevnění (Měsíce 9–10)

**Cíl:** Kurační fronty, základní učící smyčka, provozní telemetrie, zálohy, bezpečnostní kontrola.

**Technické kroky:**
1. Implementovat kurační fronty (publikovat automaticky jen schéma-compliant záznamy s nízkým dopadem).
2. Implementovat základní učící smyčku (zkušenost = naměřená přesnost typu kroku).
3. Přidat provozní telemetrii (latence, chybovost, využití GPU, počet kroků).
4. Implementovat zálohování databáze a ledgeru (šifrované, pravidelné).
5. Proveď bezpečnostní kontrolu (auditní log přístupů, šifrování v klidu, tenant isolation, prompt injection obrana).
6. Implementovat úrovně autonomie L0–L3 jako konfigurovatelnou politiku.

**Dodávky:** Kurační fronty, učící smyčka, telemetrie, zálohy, bezpečnostní audit.

**Rizika:** Únik dat, prompt injection z nahraných dokumentů, selhání Ollamy/GPU.  
**Dopad:** Dokumenty vždy jako data, nikdy instrukce; oddělené kontexty; fronta úloh, timeouty, circuit breaker, fallback na menší model.

### Fáze 5 – Pilot a rezerva (Měsíce 11–12)

**Cíl:** Pilot s design partnerem (jedna výrobní firma), rezerva 20–25 % času na zpoždění.

**Technické kroky:**
1. Nasadit serverovou verzi u design partnera (Docker, PostgreSQL, tenant isolation).
2. Proveď pilot s reálnými A3 případy, zpětnou vazbou a učící smyčkou.
3. Opravit chyby nalezené v pilotu, optimalizovat latenci.
4. Připravit dokumentaci pro zákazníka a správce systému.

**Dodávky:** Provozní pilot, zpráva z pilotu, dokumentace.

**Rizika:** Nedostatek design partnera; vlastníctví a důvěrnost A3 dat; hardware zákazníka se liší od vývojového stroje.  
**Dopad:** Model je vždy konfigurace, nikoli předpoklad v kódu; anonymizace je povinným krokem ingestion.

### Odložené za rok 1

Datové konektory a ERP, monitorovací případy a Firemní rentgen, multi-tenant a SSO, španělština, FaceModel packs, plná vizuální simulační dílna, HR a finance jako samostatní agenti.


---

## 5. Rizika a dopady (matice)

| # | Riziko | Pravděpodobnost | Dopad | Mitigace | Kdo řeší |
|---|--------|-----------------|-------|----------|----------|
| R1 | Halucinace, nepodložená tvrzení | Střední | Vysoký | Povinná evidence na claimu, verifikační vrstva, stav `unverified` viditelný, nepodložené claimy nesmí do doporučení | Vývojář |
| R2 | LLM vymýšlí čísla (falešná přesnost) | Střední | Vysoký | Deterministické výpočetní jádro, LLM jen navrhuje strukturu a vysvětluje, nikdy nevyrábí číslo | Vývojář |
| R3 | Kaskádová chyba mezi agenty | Nízká | Střední | Typované kontrakty mezi kroky, chybný claim nelze propagovat bez označení | Vývojář |
| R4 | Vyčerpání GPU / pád Ollamy | Střední | Střední | Fronta úloh, timeouty, circuit breaker, fallback na menší model, perzistentní checkpointy | Vývojář / DevOps |
| R5 | Únik dat mezi klienty | Nízká | Velmi vysoký | `tenant_id` v datovém modelu, striktní oddělení, šifrování v klidu, auditní log | Vývojář |
| R6 | Prompt injection z nahraných dokumentů | Střední | Střední | Dokumenty vždy data, nikdy instrukce; oddělené kontexty; filtrace nedůvěryhodných vstupů | Vývojář |
| R7 | Nedostatek kvalitních zdrojů pro FaceModel | Vysoká | Střední | 30–50 manuálně kurátorovaných záznamů, vlastní extrakce s odkazem na zdroj, ověření licencí | Vývojář / kurátor |
| R8 | Špatná kvalita výstupu v češtině | Vysoká | Střední | EN jako kanonický jazyk, čeština jako lokalizovaný pohled, multijazyčný embedding | Vývojář |
| R9 | Nedostatek design partnera pro pilot | Střední | Vysoký | Hledat už v měsíci 1–2, střední firma s A3 kulturou, lokální nasazení | Vývojář / business |
| R10 | Hardware zákazníka slabší než vývojový stroj | Střední | Střední | Model jako konfigurace, ne předpoklad v kódu; malé modely pro klasifikaci, 14B pro uvažování | Vývojář |

---

## 6. Návrhy a doporučení

1. **Začněte malým:** MVP obsahuje 4–5 agentů, ne jedenáct. Jedenáct agentů na lokálním hardwaru znamená vysokou latenci a kaskádová rizika.
2. **EN jako kanonický:** Vnitřní uvažování a prompty v angličtině, výstup překládán jako samostatný krok s kontrolou terminologie.
3. **Model jako konfigurace:** Nikdy nehardcodovat konkrétní model; vždy volitelný přes Model Router.
4. **Durable execution od prvního dne:** Checkpointy na každý krok, případ pokračuje po restartu.
5. **Člověk v smyčce:** Začínat na L0–L1; úroveň autonomie roste pouze podle naměřené spolehlivosti z evaluace.
6. **Regresní evaluace v CI:** Při každé změně promptu nebo modelu spustit sadu zlatých případů, aby nedošlo k degradaci kvality.
7. **Anonymizace povinná:** Vstupní krok ingestion pipeline, před uložením do znalostní báze.

---

## 7. Definice hotovo (DoD) pro každou fázi

- Kód je naprogramován, pročten a kompiluje/ běží.
- Unit testy a evaluační testy pro danou fázi passent v CI (pytest, tests/unit/, tests/eval/).
- Dokumentace aktualizována (architektura, API, uživatelská příručka).
- Riziková matice aktualizována.
- Zpětná vazba z design partnera (pokud適用uje) zapracována.

## 8. Quant Engine – kvantifikace (Měsíce 7–8)

Quant Engine poskytuje deterministické výpočty pro hodnocení finanční návratnosti řešení. Klíčové principy:

- **LLM nikdy nevyrábí čísla** – všechny výpočty jsou deterministické a plně auditovatelné.
- **Vstupy pocházejí z dat klienta nebo explicitně označených předpokladů** (Assumption).
- **Výsledky jsou sledovatelné** – každý výpočet obsahuje cash flow, NPV, payback období a citlivostní analýzu.

### 8.1 Komponenty

| Soubor | Třída | Popis |
|--------|-------|-------|
| `src/quant/engine.py` | `QuantEngine` | Hlavní vstup – compute_roi (ROI, NPV, payback, cash flow) a sensitivity (citlivostní analýza) |
| `src/quant/monte_carlo.py` | `MonteCarlo` | Monte Carlo simulace nad Quant Enginem – distribuce ROI, pravděpodobnost kladného ROI, percentily |
| `src/quant/sensitivity.py` | `SensitivityAnalyzer` | Citlivostní analýza – jak se změna vstupního předpokladu promítne do ROI |
| `src/quant/assumption_graph.py` | `AssumptionGraph` | Graf předpokladů s přepočtem dotčených větví při změně hodnoty |

### 8.2 compute_roi

Vstupní klíče: `investment`, `annual_return`, `years`, `discount_rate`.

Výstup obsahuje: `roi` (%), `npv`, `payback_years`, `total_return`, `cash_flow` (pole s ročním cash flow, kumulací a NPV příspěvkem), `status`.

Chybové stavy: `investment <= 0` vrací `status: "error: investment must be > 0"`.

### 8.3 Citlivostní analýza

Vstup: `base_case` + seznam `variations` (každá s `name` a `changes`). Výstup obsahuje `base_roi`, `base_npv` a pro každou variaci `roi`, `npv`, `roi_delta`, `payback_years`.

### 8.4 Monte Carlo simulace

Vstup: `investment_range`, `annual_return_range`, `years`, `discount_rate_range`, `iterations`, volitelný `seed` pro determinismus.

Výstup: `positive_roi_probability` (%), `roi_min/max/median/p10/p90`, `npv_min/max`, všechny simulované výsledky.

### 8.5 Graf předpokladů

Umožňuje registrovat předpoklady se závislostmi (`depends_on`). Při změně hodnoty předpokladu (`recompute`) se vrátí seznam všech ovlivněných předpokladů (rekurzivní průchod závislostmi). Ochrana proti cyklickým závislostem přes visited množinu.

### 8.6 API endpointy

| Endpoint | Metoda | Popis |
|----------|--------|-------|
| `/roi` | POST | Vypočítá deterministický ROI |
| `/sensitivity` | POST | Citlivostní analýza pro změny předpokladů |
| `/monte-carlo` | POST | Monte Carlo simulace distribuce výsledků |
| `/assumptions` | POST | Registrace nového předpokladu do grafu |
| `/assumptions/{assumption_id}/recompute` | POST | Změna hodnoty předpokladu a vrácení ovlivněných větví |

---

### Stav testovacího harnessu (Měsíce 2–3 – walking skeleton)

Implementováno v rámci walking skeletonu:

| Soubor | Testy | Popis |
|--------|-------|-------|
| `tests/unit/test_case.py` | 7 | Case model, CaseStatus, CaseStep, claims, recommendations |
| `tests/unit/test_ledger.py` | 7 | Append-only ledger, tabulka, dotazování podle case_id |
| `tests/unit/test_engine.py` | 6 | WorkflowEngine, checkpointy, obnova po selhání, ledgerové události |
| `tests/unit/test_settings.py` | 3 | Načtení modelové konfigurace z configs/models.yaml |
| `tests/unit/test_agent_schemas.py` | 8 | Pydantic schémata všech pěti agentů, validace rozsahů |
| `tests/unit/test_framer_mocked.py` | 2 | FramerAgent s mocknutým Ollama |
| `tests/unit/test_diagnostician_mocked.py` | 2 | DiagnosticianAgent s mocknutým Ollama |
| `tests/unit/test_evidence_retriever.py` | 2 | EvidenceRetrieverAgent s/bez retrieveru |
| `tests/unit/test_solution_designer_mocked.py` | 2 | SolutionDesignerAgent s mocknutým Ollama |
| `tests/unit/test_verifier_mocked.py` | 2 | VerifierAgent s mocknutým Ollama |
| `tests/eval/test_golden_a3.py` | 6 | Zlaté A3 případy (Framer, Diagnostician, SolutionDesigner, Verifier, engine) |
| `tests/eval/conftest.py` | – | Fixtures: 2 zlaté případy (golden-a3-001, golden-a3-002) |

### Stav testovacího harnessu (Měsíce 4–6 – znalostní jádro)

Nově přidáno v rámci FaceModel schématu, A3 ingestion pipeline, hybridního retrievalu a verifikační vrstvy:

| Soubor | Testy | Popis |
|--------|-------|-------|
| `tests/unit/test_face_model.py` | 8 | FaceModelCreate/Update/Response/List/Filter, validační meze |
| `tests/unit/test_ingestion.py` | 13 | A3Ingestor (text/markdown/JSON/soubor), chunking, FaceModel creation, chybové stavy |
| `tests/unit/test_retrieval.py` | 9 | HybridRetriever (keyword, sémantika, hybrid, persistence, prázdné výsledky) |
| `tests/unit/test_verification_layer.py` | 10 | VerificationLayer (assumption, work_model, client_data, face_model, edge cases) |

### Stav testovacího harnessu (Měsíce 7–8 – kvantifikace a Red Team)

Nově přidáno v rámci Quant Enginu (ROI, citlivost, Monte Carlo, graf předpokladů):

| Soubor | Testy | Popis |
|--------|-------|-------|
| `tests/unit/test_quant_engine.py` | 13 | QuantEngine compute_roi (základní, chybové stavy, cash flow, payback), citlivostní analýza (variace, prázdné base_case, delta) |
| `tests/unit/test_monte_carlo.py` | 12 | MonteCarlo simulate (distribuce, determinismus se seedem, rozsahy, pravděpodobnost kladného ROI, nulové iterace) |
| `tests/unit/test_assumption_graph.py` | 9 | AssumptionGraph (přidání, závislosti, set, recompute, ovlivněné větve, cykly) |

**Celkem:** 193 testů (98 unit + 22 eval + 73 security), všechny procházejí.

### Stav testovacího harnessu (Měsíce 7–8 – Red Team / bezpečnostní testy)

Nově přidáno v rámci bezpečnostního testování:

| Soubor | Testy | Popis |
|--------|-------|-------|
| `tests/security/test_quant_adversarial.py` | 32 | ROI, citlivost, Monte Carlo, AssumptionGraph vůči neplatným vstupům, NaN/Infinity, extrémním rozsahům, injekčním payloadům |
| `tests/security/test_ingestion_security.py` | 10 | A3 ingestor – invalidní JSON, hluboké vnoření, chybějící soubory, binární data, REDOS, injection |
| `tests/security/test_retrieval_security.py` | 12 | HybridRetriever – neplatné dotazy, injection ID, poškozená DB, prázdné výsledky |
| `tests/security/test_verification_security.py` | 8 | VerificationLayer – neplatné claims, injection source/face_model_id, hromadné texty |
| `tests/security/test_anonymization_security.py` | 9 | Anonymizer – redakce PII, ochrana před ReDoS, injection do řetězců |
| `tests/security/test_models_security.py` | 6 | Pydantic FaceModel a Case modely – injection jako data, limity accuracy/limit/offset |

**Celkem:** 73 testů (bezpečnostní / adversarial), všechny procházejí.

