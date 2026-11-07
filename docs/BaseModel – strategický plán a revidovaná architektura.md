# BaseModel – strategický plán a revidovaná architektura

Pracovní verze 1.0 · podklad: černopisy a základní popis myšlenky · cíl: posunout návrh na vyšší úroveň, s důrazem na robustnost a automatizaci

## 1. Shrnutí a verdikt

Základní myšlenka je silná a dá se obhájit: **lokální, auditovatelná platforma pro rozhodování ve firmách, která místo „odpovědi chatbota“ produkuje strukturovanou analýzu opřenou o ověřené vzory (WorkModel / FaceModel)**. Diferenciace oproti běžným firemním chatbotům je reálná, ale jen pokud se splní jedna podmínka, která v původním návrhu chybí:

> **Každé tvrzení, číslo a doporučení v systému musí být dohledatelné: buď na důkaz ve WorkModelu, nebo na data klienta, nebo na explicitně označený předpoklad.**

Bez toho se systém změní v „poradenské divadlo“: profesionálně vypadající výstupy (skóre jistoty 0,82, simulace +12 % kapacity, rentgen firmy 72 %), za kterými nestojí nic ověřitelného. Je to největší riziko celého projektu a zároveň největší příležitost, protože právě tohle běžné AI nástroje nedělají.

Tři teze tohoto plánu:

1. **Hodnota není v modelu ani v počtu agentů, ale ve třech věcech:** kvalitě a struktuře WorkModelu, deterministickém řízení procesu a ověřování výstupů.
2. **Agenti nejsou „osobnosti“, ale typované funkce** se vstupním a výstupním schématem, vlastními nástroji a vlastním rozsahem znalostí. Řízení toku je deterministické (workflow engine), LLM se používá uvnitř kroků, ne jako dirigent.
3. **Robustnost a automatizace jsou architektonické vrstvy od prvního dne**, ne pozdější vylepšení: durable execution, validace schémat, evaluační sada, automatická kurace znalostí a zpětná vazba z reálných výsledků.

## 2. Kritická revize původního návrhu

Původní návrh je dobrá vize. Pro přechod do realizace je ale potřeba pojmenovat slabá místa.

### 2.1 Co je silné a co zachovat

- **Case-centrické UX** (uživatel řeší případ, ne konverzaci s AI) je správný směr.
- **Tým rolí s různými pohledy** má smysl, pokud se pohledy skutečně liší (viz 2.2).
- **Oponent (Devil's Advocate)** a **argumentace PRO/PROTI** zvyšují důvěryhodnost.
- **Strukturovaná společná znalostní zóna** místo dlouhých textů je správná volba.
- **Výměnitelný LLM, trvalá hodnota ve znalostní bázi** je strategicky správný pohled.

### 2.2 Slabá místa a rizika

**A) Jeden model v různých rolích = prompt-diverzita, ne nezávislé názory.** Stejný model s jedenácti prompty sdílí stejné předsudky a slepá místa. Chyby jsou korelované: pokud model něco špatně „ví“, špatně to budou vědět všichni agenti. Skutečnou diverzitu dává až odlišný vstup: jiná data, jiné nástroje, jiná omezení, ideálně i jiný model. Jedenáct agentů navíc na lokálním hardwaru znamená vysokou latenci a vysoké riziko kaskádových chyb.

**B) Čísla vygenerovaná LLM nejsou data.** Ukázky typu „+12 % kapacita, −18 % cashflow“, „confidence 0,82“ nebo „Procesy 72 %“ by LLM vymýšlel. To je falešná přesnost. Simulace musí běžet v deterministickém výpočetním jádru s parametry z dat klienta nebo z označených předpokladů. LLM smí navrhnout strukturu modelu a vysvětlit výsledek, ale nikdy ne vyrobit číslo.

**C) Sebehodnocená „jistota“ není kalibrovaná.** Model, který napíše confidence 0,85, nevypovídá o pravděpodobnosti správnosti. Je třeba složené skóre z vlastností důkazů (kvalita zdrojů, počet nezávislých zdrojů, shoda napříč běhy a modely, úplnost dat, výsledek verifikace) a to později kalibrovat podle skutečných výsledků.

**D) FaceModely slavných firem (Toyota, Google, Tesla) jsou zrádné.** Veřejně dostupné příběhy trpí survivorship biasem, jsou zjednodušené a těžko přenositelné. Doporučení „udělejte to jako Toyota“ je často nepoužitelné pro firmu o 80 lidech. Každý FaceModel proto musí nést **kontext, mechanismus úspěchu, předpoklady a podmínky přenositelnosti**, ne jen výsledek. Přibývá také právní stránka: původ dat, autorská práva, licence.

**E) Cold-start WorkModelu.** Prázdná databáze = prázdný produkt. Je potřeba strategie plnění: automatická extrakce z veřejných zdrojů s lidskou kurací, vlastní metodiky (Lean, TOC, OKR, ISO, ITIL…) jako první vrstva a zpětná vazba z reálných případů jako dlouhodobý zdroj.

**F) „Firemní rentgen“ bez dat je kosmetika.** Procentní skóre oblastí firmy má smysl jen tehdy, když vzniká z reálných dat (připojené zdroje, dotazníky, metriky). Jinak je to ozdobný graf. Systém musí umět říct „nedostatek dat“.

**G) Chybí zpětná vazba z reality.** Návrh končí doporučením. Skutečná hodnota (a skutečný příkop) vzniká, až když systém sleduje: bylo doporučení realizováno, jaký byl výsledek a co se z toho má naučit.

**H) Nejasný zákazník a prostředí nasazení.** SME, střední firma, nebo korporát? Konzultant jako uživatel, nebo vedení firmy? Lokální (on-prem) nasazení je silný argument (soukromí dat), ale omezuje kvalitu modelu. Tohle je nutné rozhodnout dříve, než se zafixuje architektura.

## 3. Revidovaná vize a principy produktu

**Pozicování:** *Evidence-grounded decision workbench* – pracovní stůl pro analýzu problémů a rozhodnutí, který skládá analýzu z ověřených vzorů, spočítaných scénářů a explicitně vedené argumentace. Není to orákulum, ale transparentní analytický partner.

Principy, ze kterých se odvozují všechna další rozhodnutí:

1. **Groundedness first** – žádné tvrzení bez evidence, dat nebo označeného předpokladu.
2. **Deterministické jádro, pravděpodobnostní okraj** – tok procesu, výpočty a validace jsou deterministické; LLM dělá porozumění, syntézu a návrhy.
3. **Typované kontrakty** – každý krok má schéma vstupu a výstupu; nevalidní výstup se nikdy nepropaguje dál.
4. **Automatizuj vše, zabraňuj tomu, co je riskantní** – automatizace s řízenými úrovněmi autonomie a lidskými branami.
5. **Reprodukovatelnost** – každý případ lze přehrát se zafixovanými verzemi modelu, promptů a znalostí.
6. **Učení z výsledků** – systém měří, co se po doporučeních skutečně stalo.
7. **Lokálnost jako vlastnost** – data klienta neopouštějí infrastrukturu, pokud to klient výslovně nepovolí.

## 4. Cílová architektura

### 4.1 Vrstvy

```
Frontend (Case workspace)
        |
API / Case Service  ── stav případu, verze, audit log
        |
Workflow Engine (durable, deterministický DAG / state machine)
        |
   ┌────┼──────────────┬───────────────┬──────────────┐
   |    |              |               |              |
Agenti  Quant Engine   Knowledge Engine  Verifikace     Model Router
(typ.   (Python,       (WorkModel:       (schéma,       (Ollama, více
funkce) deterministické graf+vektor+     citace,        modelů, fronty,
        simulace)      relační DB)       čísla,         fallbacky)
                                         rozpory)
        
        └────────── Case Evidence Ledger (sdílená znalostní zóna případu) ─────────┘
                                  |
                         Synthesizer (Decision Architect)
                                  |
                         Report + Argument Graph
```

### 4.2 Klíčové komponenty

**Workflow Engine.** Případ prochází definovaným pipeline: *Intake → Framing → Diagnóza → Evidence retrieval → Návrh variant → Kvantifikace → Red team → Verifikace → Syntéza → Review*. Každý krok je idempotentní, má timeout, budget (tokeny, čas, počet pokusů), checkpoint a definované chování při selhání. Konverzace mezi agenty v otevřené smyčce („agenti si povídají“) se nepoužívá, protože je nedeterministická, drahá a špatně laditelná. Místo toho agenti čtou z ledgeru a zapisují do něj.

**Case Evidence Ledger (náhrada „obecné znalostní zóny“).** Jednotka je *claim* (tvrzení), ne text:

```json
{
  "claim_id": "c-0142",
  "type": "finding | assumption | metric | risk | option",
  "statement": "Silná závislost na jediném dodavateli komponenty X",
  "produced_by": "diagnostician@v3",
  "evidence": [
    {"kind": "client_data", "ref": "doc-12#table-3"},
    {"kind": "facemodel", "ref": "fm-0457", "grade": "B"}
  ],
  "assumptions": ["a-007"],
  "support_score": 0.64,
  "status": "verified | disputed | unverified",
  "depends_on": ["c-0101"]
}
```

Graf závislostí mezi claimy (`depends_on`) je zásadní pro automatizaci: když uživatel změní předpoklad, systém přepočítá jen dotčené větve, ne celý případ.

**Quant Engine.** Deterministická výpočetní vrstva v Pythonu: ROI/NPV/payback, analýza citlivosti, Monte Carlo, základní system dynamics, front a kapacitní modely (Little's law), Pareto a SPC z dat. Agent (LLM) navrhuje strukturu modelu a parametry s odůvodněním, engine počítá, agent výsledek vysvětluje. Výstupem jsou **rozsahy a distribuce**, ne jedno číslo, vždy s označením: *z dat klienta / z benchmarku / z předpokladu*.

**Knowledge Engine (WorkModel).** Hybridní úložiště: relační metadata + graf vztahů + vektorový index. Retrieval kombinuje filtr na kontext (obor, velikost, zralost), grafový průchod (alternativy, předpoklady, konflikty) a sémantické vyhledávání, s rerankingem. Důležité je **vyhledávání analogií podle struktury problému**, ne podle klíčových slov. Podrobně v kapitole 6.

**Verifikační vrstva.** Převážně deterministická, s malým podílem LLM:

- validace JSON schématu,
- kontrola, že citované evidence reálně existují a podporují tvrzení,
- kontrola číselné konzistence (součty, jednotky, rozsahy),
- detekce rozporů mezi claimy,
- kontrola, že každé doporučení má evidenci a že všechna rizika mají mitigaci nebo je označena jako akceptovaná.

**Model Router.** Různé kroky potřebují různé modely: malý rychlý model pro klasifikaci a extrakci, větší model pro uvažování a syntézu, embedding model pro retrieval. Router řeší fronty, souběžnost (lokální GPU je úzké hrdlo), fallbacky a verzování. Pro důležité kroky lze použít **dvojí běh nebo dva různé modely** a porovnat výsledky, což je levnější cesta ke skutečné diverzitě než jedenáct rolí.

## 5. Redesign týmu agentů

### 5.1 Od 11 rolí k pipeline s „čočkami“

Původních 11 rolí je dobrý konceptuální katalog, ale jako 11 samostatných LLM volání je to neekonomické a křehké. Doporučení: **rozlišit funkční agenty (vždy běží) a analytické čočky (aktivují se podle typu případu)**.

**Funkční jádro (MVP):**

1. **Framer** (Business Analyst) – převede zadání na strukturovaný case: cíl, KPI, omezení, nejasnosti. Umí položit doplňující otázky; pokud chybí kritická data, případ se zastaví v bráně.
2. **Diagnostician** (Root Cause + Lean + Kaizen) – příčiny a plýtvání. Používá šablony metod (5 Why, Ishikawa, 7 plýtvání, Pareto nad daty). Výstup: claimy typu *finding* s evidencí.
3. **Evidence Retriever** (Benchmark Expert) – dotazuje WorkModel, vrací analogie včetně podmínek přenositelnosti a poctivého hodnocení, kde analogie neplatí.
4. **Solution Designer** (Process Architect + Innovation) – generuje varianty (konzervativní, rychlá, nízkonákladová, transformační), včetně nekonvenčních (TRIZ, first principles).
5. **Quant Analyst** (Financial) – tenká LLM vrstva nad Quant Engine; navrhuje model, ne čísla.
6. **Red Team** (Risk Manager + Devil's Advocate) – útočí na každou variantu a na předpoklady; musí vyrobit konkrétní, ověřitelná rizika, ne obecné fráze.
7. **Synthesizer** (Decision Architect) – nevymýšlí; skládá z ledgeru, řeší konflikty podle pravidel, řadí priority a generuje report a argumentační graf.

**Aktivovatelné čočky (podle typu případu):** Strategic Advisor (horizont 1/3/5 let), Compliance/Legal, HR/People, IT/ITIL, Supply Chain/TOC, Product/Design thinking. Každá čočka = konfigurace (prompt, šablony, relevantní metodiky, vyhrazený rozsah WorkModelu), ne nová architektura. Přidání čočky je tak otázka dat, ne kódu.

### 5.2 Kontrakt agenta

Každý agent je definován deklarativně (verzovaný soubor):

- **účel a rozsah** (co řeší a co ne),
- **vstupní a výstupní schéma**,
- **povolené nástroje** a rozsah čtení z WorkModelu,
- **model a parametry** (teplota, kontext),
- **budget** (tokeny, čas, počet retry),
- **kritéria úspěchu** (kontroly, které musí výstup splnit),
- **chování při selhání** (retry s opravou → fallback model → označit mezeru a pokračovat).

Výhoda: agenty lze testovat izolovaně, verzovat a vyměňovat, a systém lze rozšiřovat bez zásahu do jádra.

### 5.3 Jak zajistit skutečnou diverzitu pohledů

- odlišné **vstupy** (každý agent vidí jiný výřez dat a jiné části WorkModelu),
- odlišné **metody** (strukturované šablony místo volného generování),
- kritické kroky **dvakrát s různými modely** nebo s různou teplotou a porovnání,
- Red Team má **motivaci vyvracet**, a ne navazovat na předchozí text (izolovaný kontext, vidí jen claimy).

## 6. WorkModel a FaceModel – návrh znalostní báze

Tohle je hlavní příkop produktu, takže si zaslouží největší návrhové úsilí.

### 6.1 Čtyři vrstvy znalostí

1. **Metodiky** (Lean, Kaizen, Six Sigma, TOC, OKR, PMBOK, ISO, ITIL…) – principy, nástroje, vstupní podmínky, typické chyby aplikace.
2. **Vzory (patterns)** – opakující se dvojice *problém → zásah → výsledek* s mechanismem.
3. **Případové studie (FaceModely)** – konkrétní firemní případy, s kontextem a evidencí.
4. **Interní historie klienta** (privátní vrstva) – vlastní případy, doporučení a naměřené výsledky. Dlouhodobě nejcennější, protože je jedinečná pro každého klienta.

### 6.2 Schéma FaceModelu (návrh)

- **identita:** id, název, typ (metodika / vzor / případ / interní), verze
- **kontext:** obor, velikost firmy, zralost, geografie, časové období, omezení
- **problémový vzor:** strukturovaný popis problému (ne marketingový slogan)
- **zásah:** co se konkrétně změnilo
- **mechanismus:** *proč* to fungovalo (nejdůležitější pole pro přenositelnost)
- **předpoklady a podmínky přenositelnosti:** kdy to fungovat nebude
- **parametry a KPI:** hodnoty včetně rozsahů, jednotek a časového horizontu
- **výsledky a selhání:** výsledky i vedlejší efekty a známé neúspěchy
- **evidence:** zdroje, datum, **stupeň kvality A–D** (primární data / audit / sekundární analýza / anekdota)
- **vztahy v grafu:** `alternative_to`, `prerequisite_of`, `conflicts_with`, `implements`, `evolved_from`
- **governance:** licence/původ, stav revize, vlastník, datum příští revize (TTL)

### 6.3 Automatizovaná ingestion pipeline

```
Zdroj → sběr → extrakce (LLM do schématu) → validace schématu
      → deduplikace/sloučení → skórování kvality evidence
      → fronta pro kurátora (jen nejisté/významné) → publikace
      → periodická revize (TTL) a detekce zastarání
```

Pravidla: nic se nepublikuje bez původu; nízká kvalita evidence se publikuje jen s viditelným označením; kurátor řeší výjimky, ne vše. Cíl je lidskou práci minimalizovat, ne eliminovat u obsahu, na kterém stojí důvěryhodnost produktu.

### 6.4 Strategie plnění (řešení cold-startu)

1. **Fáze 1:** ručně kurátorovaných 30–50 kvalitních záznamů: metodiky a vzory z veřejně známých a licenčně čistých zdrojů. Raději méně a kvalitně.
2. **Fáze 2:** poloautomatická ingestion z veřejných zdrojů s kurací.
3. **Fáze 3:** interní vrstva z reálných případů klientů a zpětná vazba z výsledků (viz 8.5).
4. **Později:** komerční „FaceModel packs“ pro obory (výroba, logistika, SaaS…).

Pozor na právní stránku: nekopírovat texty, ukládat vlastní strukturovanou extrakci s odkazem na zdroj; ověřit licence před komerčním použitím.

## 7. Robustnost – návrhový rámec

Robustnost se nezajistí jedním opatřením, ale vrstvením. Níže mapa selhání a protiopatření.

### 7.1 Mapa rizik a opatření

- **Halucinace a nepodložená tvrzení** → povinné evidence na claimu, verifikační vrstva, stav `unverified` viditelný v UI a v reportu; nepodložené claimy nesmí do doporučení.
- **Rozbitý nebo neplatný výstup modelu** → výstup vynucený schématem (Ollama podporuje strukturovaný výstup přes JSON schéma), validace, automatická oprava (retry s chybovou zprávou), po vyčerpání pokusů fallback model a označení mezery.
- **Pád nebo pomalost Ollamy / vyčerpání GPU** → fronta úloh, timeouty, circuit breaker, fallback na menší model, perzistentní checkpointy (případ pokračuje po restartu).
- **Smyčky a explozivní náklady** → pevné budgety kroků, žádné neomezené agentní smyčky, limity hloubky.
- **Přetečení kontextu** → agenti nepracují nad surovým textem, ale nad claimy a výřezy; sumarizace deterministická tam, kde to jde.
- **Nedeterminismus** → teplota nízká u extrakce a verifikace, uložená konfigurace běhu, možnost přehrání případu s fixními verzemi.
- **Prompt injection z nahraných dokumentů** → dokumenty jsou vždy *data*, nikdy instrukce; oddělené kontexty, agenti s dokumenty nemají nástroje s vedlejšími efekty, filtrace a označování nedůvěryhodných vstupů.
- **Únik dat** → lokální běh, přísné oddělení klientů (tenant isolation), šifrování v klidu, auditní log přístupů.
- **Rozpory mezi agenty** → explicitní pravidla řešení (priorita podle kvality evidence, ne podle „přesvědčivosti“), nevyřešené rozpory se zobrazí uživateli, nikoli skryjí.
- **Zastaralá znalost** → TTL na záznamech, automatická detekce stáří, označení ve výstupu.
- **Kaskádová chyba** → typované kontrakty mezi kroky; chybný claim nelze propagovat dál bez označení.
- **Degradace kvality po změně promptu nebo modelu** → regresní evaluace v CI (viz 9).

### 7.2 Degradace místo selhání

Systém musí umět odevzdat **částečný, poctivě označený výsledek**: pokud selže kvantifikace, report vznikne a jasně uvádí „finanční analýza nedokončena z důvodu X“. Selhání jednoho kroku nesmí zahodit práci ostatních.

### 7.3 Úrovně autonomie

Každému kroku se přiřadí úroveň:

- **L0** – jen návrh, vše schvaluje člověk,
- **L1** – automatické provedení, člověk kontroluje výsledek,
- **L2** – automatické provedení, člověk jen při nízkém skóre nebo rozporu,
- **L3** – plně automatické, jen audit.

Na začátku jsou téměř všechny kroky L0–L1; úroveň se zvyšuje jen na základě naměřené spolehlivosti z evaluace.

## 8. Automatizace – pět úrovní

**8.1 Automatizace procesu případu.** Od zadání po report bez ručního zásahu: intake, spuštění pipeline, retry, verifikace, generování reportu. Člověk vstupuje jen v definovaných branách (chybějící kritická data, nízké skóre, rozpor, schválení).

**8.2 Automatizace znalostí.** Ingestion, extrakce, deduplikace, skórování, detekce zastarání, fronty pro kurátora, automatické refresh embeddingů a grafu při změnách.

**8.3 Automatizace kvality.** Evaluační sada běží automaticky při každé změně promptu, modelu nebo znalostní báze. Obsahuje zlaté případy (golden cases), kontroly schémat a číselné konzistence, adversariální testy (injection, nekonzistentní data) a kalibrovaného LLM soudce (kalibrovaného proti lidským hodnocením, ne naslepo).

**8.4 Automatizace provozu.** Health checks Ollamy a modelů, správa verzí modelů, zálohy, telemetrie (latence, selhání, tokeny na případ), alerting, automatické čištění a archivace.

**8.5 Učící smyčka (nejdůležitější dlouhodobě).** Doporučení → *bylo realizováno?* → *jaké KPI se skutečně změnily?* → zápis do interní vrstvy WorkModelu → **kalibrace skóre jistoty a vah evidence**. Systém se tak postupně učí, které analogie a metody u daného klienta či oboru skutečně fungují. Tohle je to, co nelze snadno zkopírovat.

**Rozšíření:** monitorovací případy spouštěné plánovačem a datovými konektory (CSV/Excel/DB/ERP): rentgen firmy se aktualizuje sám a upozorní, když se KPI vychýlí.

## 9. Měření kvality a skóre důvěry

### 9.1 Složené skóre podpory (nahrazuje „confidence 0,82“)

Skóre claimu vzniká z měřitelných složek:

- kvalita evidence (A–D) a počet **nezávislých** zdrojů,
- podíl tvrzení podložených daty klienta oproti předpokladům,
- shoda napříč běhy / modely (self-consistency),
- úplnost vstupních dat,
- výsledek verifikace a výsledek útoku Red Teamu (přežilo tvrzení kritiku?).

V UI se ukazuje **rozsah a typ původu**, ne jedno číslo. Skóre se časem kalibruje podle výsledků z učící smyčky.

### 9.2 KPI produktu a systému

- **Groundedness:** % claimů s validní evidencí; cíl nad 95 % u doporučení.
- **Validita výstupů:** % kroků, které prošly schématem bez retry.
- **Číselná konzistence:** % reportů bez chyb v číslech.
- **Přijetí lidmi:** podíl doporučení, která uživatel přijal nebo upravil málo.
- **Slepé srovnání** s jednoduchým baseline (jeden dobrý prompt na stejný případ) hodnocené experty. **Pokud multiagentní pipeline není prokazatelně lepší než baseline, přestavuje se, ne rozšiřuje.**
- **Čas a náklady na případ** (latence, tokeny, GPU čas).
- **Úspěšnost doporučení** (podle učící smyčky), až bude dost dat.

Klíčový experiment už ve Fázi 0: ablační testy (bez WorkModelu, bez Red Teamu, bez verifikace) ukážou, co skutečně přidává hodnotu.

## 10. UX – revidovaný koncept

Zachovat: case-centrický model. Změnit: z „ukázat hezké dashboardy“ na **„ukázat, na čem co stojí“**.

**Principy UX:**

1. **Každé číslo a tvrzení je klikatelné** → zdroj, data nebo předpoklad.
2. **Předpoklady jsou first-class objekt.** Panel předpokladů je editovatelný; změna předpokladu přepočítá jen dotčené claimy (využívá graf `depends_on`).
3. **Pravdivý stav zpracování** místo dekorativních progress barů: skutečné kroky pipeline, jejich stav, trvání a případná selhání.
4. **Poctivost o nejistotě:** rozsahy, označení původu, stav `unverified`, „nedostatek dat“.
5. **Tři režimy hloubky:** *Rychlý* (minuty, jádro 3 agenti), *Standardní*, *Hluboký* (včetně dvojího běhu a plného red teamu).

**Hlavní obrazovky:**

- **Dashboard případů** – stav, brány čekající na uživatele, upozornění z monitoringu.
- **Intake** – kombinace řízeného formuláře a krátkého dialogu; nahrání dat a dokumentů; systém se aktivně ptá na to, co chybí.
- **Evidence Board** – živé claimy seskupené podle typu, filtr podle stavu ověření.
- **Argumentační graf** – claimy a vztahy podpora/útok mezi nimi (strukturovaná argumentace, např. styl IBIS/Toulmin), rozbalování větví, u každého uzlu evidence.
- **Simulační dílna** – posuvníky nad parametry Quant Engine, výstup jako rozsahy a distribuce, s viditelným původem každého parametru.
- **FaceModel Explorer** – procházení znalostní báze včetně podmínek přenositelnosti a kvality evidence.
- **Firemní rentgen** – pouze nad připojenými daty; bez dat zobrazí „nedostatek dat“ místo vymyšleného skóre.
- **Report** – jednostránkové Executive Summary, priority P1–P3, rizika, ROI v rozsazích, předpoklady, otevřené rozpory; export do PDF/DOCX.
- **Follow-up** – po realizaci sledování výsledků (vstup do učící smyčky).

## 11. Technologický návrh (výchozí varianty)

Konkrétní volba záleží na cílovém nasazení (viz otevřené otázky). Doporučené výchozí řešení:

- **Backend:** Python (FastAPI) – přirozené prostředí pro LLM, výpočty (NumPy/SciPy), simulace a ingestion.
- **Workflow / durable execution:** pro MVP vlastní lehká state machine nad databází (stav kroku, retry, checkpointy); později Temporal nebo podobný engine, pokud poroste složitost.
- **Úložiště:** PostgreSQL (relační data, audit, ledger) + pgvector pro vektory; graf vztahů zpočátku jako tabulky hran (dedikovaná grafová DB až při prokázané potřebě). Pro velmi lehké MVP stačí SQLite + vektorové rozšíření.
- **LLM:** Ollama s více modely přes Model Router; strukturovaný výstup přes JSON schéma; samostatný embedding model. Kvalita **češtiny** je kritická vlastnost při výběru modelů i embeddingů – nutné testovat již ve Fázi 0.
- **Frontend:** React/TypeScript; vizualizace grafů (graf argumentů, stromy) a formulářové simulace.
- **Kvalita a provoz:** evaluační harness v CI, verzované prompty a konfigurace agentů (jako kód), structured logging a metriky, zálohy.

## 12. Roadmapa s rozhodovacími branami

Časové odhady předpokládají malý tým (1–3 lidé); jsou orientační.

**Fáze 0 – Validace (2–3 týdny).** Vybrat 2–3 cílové use-case a cílového zákazníka. Vytvořit 5–10 reálných případů (zlaté případy) a ručně k nim připravit „expertní“ reporty. Rychlý prototyp pipeline pomocí řetězených promptů a **ablační test proti jednomu promptu**. Otestovat češtinu lokálních modelů na hardwaru, který bude k dispozici. *Brána:* je rozdíl v kvalitě oproti baseline viditelný a měřitelný? Ano → pokračovat; ne → upravit koncept.

**Fáze 1 – Walking skeleton (4–6 týdnů).** Case Service, workflow engine s checkpointy, Evidence Ledger, kontrakty agentů, Framer + Diagnostician + Synthesizer, validace schémat, jednoduchý report, evaluační harness od prvního dne, základní UI (případy, board, report). *Brána:* end-to-end případ proběhne opakovaně bez ručního zásahu, nad zlatými případy stabilní validita výstupů.

**Fáze 2 – Znalostní jádro (6–8 týdnů).** Schéma FaceModelu, ingestion pipeline, 30–50 kurátorovaných záznamů, hybridní retrieval, Evidence Retriever, verifikační vrstva (citace, rozpory), FaceModel Explorer. *Brána:* groundedness doporučení nad stanoveným prahem; benchmark agent prokazatelně zlepšuje kvalitu v ablaci.

**Fáze 3 – Kvantifikace a red team (6–8 týdnů).** Quant Engine, Quant Analyst, Red Team, graf předpokladů s přepočtem dotčených větví, argumentační graf, simulační dílna. *Brána:* čísla v reportech jsou plně dohledatelná; Red Team nachází věcné problémy, ne fráze.

**Fáze 4 – Automatizace a učící smyčka (6–8 týdnů).** Datové konektory, monitorovací případy, sledování výsledků doporučení, kalibrace skóre, automatizace kurace, provozní telemetrie a alerting, úrovně autonomie. *Brána:* systém běží týdny bez ručního zásahu v provozu; první kalibrační data.

**Fáze 5 – Zpevnění a pilot (6 týdnů).** Bezpečnostní audit (injection, tenant isolation, šifrování), zálohy a obnova, zátěžové testy, výkon, dokumentace; pilot u 2–3 reálných firem se sběrem výsledků. *Brána:* pilot potvrdí hodnotu (přijetí doporučení, ušetřený čas, ochota platit).

**Fáze 6 – Škálování.** Multi-tenant, oborové FaceModel packs, API/integrace, případně hybridní režim (volitelně cloudové modely pro nesenzitivní kroky), rozšiřování čoček.

## 13. Rizika projektu a mitigace

- **„Poradenské divadlo“** (působí profesionálně, ale není podložené) → principy groundedness, verifikace, poctivé UI, ablační testy, expertní slepé hodnocení.
- **Strop kvality lokálních modelů** → tiering modelů, dvojí běh u kritických kroků, deterministické jádro, které kompenzuje slabiny modelů; volitelný hybridní režim.
- **Cold-start znalostí** → kurátorované jádro, automatická ingestion s kurací, interní vrstva z reálných případů.
- **Rozsah (scope creep)** → fázování s bránami; čočky přidávat jako konfiguraci, ne nový kód.
- **Právní rizika** (autorská práva zdrojů, GDPR, odpovědnost za doporučení) → ukládat strukturovanou extrakci s původem, jasná licenční politika, disclaimery a auditní stopa, konzultace s právníkem před komercializací.
- **Konkurence** (velké platformy, konzultantské nástroje) → diferenciace přes lokálnost, auditovatelnost, interní vrstvu a učící smyčku; neřešit obecného asistenta.
- **Závislost na jednom člověku/klíčové komponentě** → dokumentace architektury, kontrakty, testy, reprodukovatelnost.
- **Latence na lokálním hardwaru** → asynchronní zpracování, režimy hloubky, fronta, menší modely pro jednoduché kroky.

## 14. Obchodní model (orientačně)

- **Licence / předplatné** na platformu (on-prem nebo privátní server).
- **FaceModel packs** (oborové balíčky znalostí) jako opakující se příjem.
- **Implementace a onboarding** (napojení dat, kalibrace na firmu) jako služba.
- **Premium:** monitoring, učící smyčka, interní znalostní vrstva.

Obchodní model je nutné potvrdit až po validaci zákazníka (Fáze 0 a pilot).

## 15. Otevřené otázky, které je třeba rozhodnout

1. **Cílový zákazník:** SME, střední firma, korporát, nebo poradenské firmy jako uživatelé?
2. **Nasazení:** desktop, firemní server, nebo hybrid? Jaký hardware (GPU, paměť) je reálně k dispozici?
3. **Jazyk:** jen čeština, nebo vícejazyčně? Jak kvalitní jsou vybrané modely a embeddingy v češtině?
4. **Zdroje FaceModelů:** co je dostupné a licenčně čisté; kdo bude kurátor?
5. **Primární use-case pro MVP:** výroba, logistika, finance, HR? (Doporučení: jedna doména, ne všechny.)
6. **Tým a časový rámec:** kolik lidí a kolik času je k dispozici?
7. **Míra autonomie:** kde je firma ochotna přijmout plně automatická rozhodnutí a kde vždy chce člověka?

## 16. Okamžité kroky (následujících 14 dnů)

1. Zafixovat cílového zákazníka a jeden primární use-case.
2. Sestavit 5–10 zlatých případů (reálné nebo realistické) včetně „referenčního“ expertního řešení.
3. Otestovat 2–3 lokální modely (kvalita, **čeština**, rychlost) na dostupném hardwaru.
4. Vytvořit prototyp pipeline (Framer → Diagnostician → Synthesizer) jako řetěz promptů a porovnat se samostatným promptem (ablace č. 1).
5. Navrhnout první verzi schématu FaceModelu a ručně vyplnit 10 záznamů, abyste zjistili, co schéma neumí zachytit.
6. Definovat kontrakt agenta a schéma claimu a zapsat je jako verzované soubory.
7. Rozhodnout o technologickém základu pro Fázi 1 podle odpovědí na otevřené otázky.

## 17. Závěr

Původní návrh má správný instinkt: *poradní tým + znalostní báze ověřených vzorů*. Aby z něj vznikl produkt, který obstojí, je potřeba tři posuny: **od „odpovědí“ k doložitelným claimům, od „AI týmu“ k deterministické pipeline s typovanými agenty, a od jednorázového doporučení k učící smyčce s měřenými výsledky.** Robustnost (validace, durable execution, degradace, evaluace) a automatizace (proces, znalosti, kvalita, provoz, učení) nejsou přídavkem, ale tělem architektury. Nejrychlejší cesta k jistotě je Fáze 0: ověřit na malém experimentu, že tento přístup skutečně překonává jednoduchý prompt, než se investuje do celé platformy.

## 18. Rozhodnutí z otevřených otázek a jejich dopad na plán

Odpovědi na kapitolu 15 mění čtyři věci: zdroj znalostí se zostřuje na A3, MVP se zužuje, nasazení se řeší jedním jádrem a roadmapa se přepočítává na jednoho vývojáře.

### 18.1 A3 případy jako páteř produktu

A3 je pro tento projekt výjimečně šťastná volba. Jeho struktura (pozadí, současný stav, cíl, analýza příčin, protiopatření, plán realizace, následná kontrola) odpovídá téměř 1:1 pipeline *Framer → Diagnostician → Solution Designer → plán → follow-up*, schématu FaceModelu i claimům.

- **A3 je vstupní, znalostní i výstupní formát.** Report produktu může být jednostránkové A3, které zákazník s lean kulturou přečte bez zaškolení.
- **FaceModel z existujícího A3 vzniká poloautomaticky:** extrakce do schématu (kontext, příčiny, protiopatření, výsledek) a kontrola kurátorem. Pole *mechanismus* a *podmínky přenositelnosti* A3 často výslovně neobsahuje, proto je extrakce označí jako odvozená a ověří se.
- **Pozice produktu se zostřuje:** *A3 problem-solving engine s důkazní základnou*, ne obecná „decision intelligence".
- **Právní poznámka:** před použitím A3 případů je nutné ujasnit vlastnictví a důvěrnost dat. Anonymizace se stává povinným krokem ingestion pipeline.

### 18.2 Zúžení MVP: výroba jako svislý řez

„Výroba, která zahrnuje logistiku, finance i HR" je správný dlouhodobý záběr, ale pro jednoho vývojáře na jeden rok příliš široký. MVP = **výrobní problem-solving v logice A3/Lean**: kvalita a vady, prostoje, plýtvání, produktivita, vnitropodniková logistika. Ostatní oblasti vstupují později jako čočky (kapitola 5), ne jako samostatní agenti:

- **Finance:** zatím jen jako Quant Engine (ROI, návratnost, citlivost).
- **Logistika:** po MVP jako čočka s vlastními metodikami (TOC, supply chain).
- **HR:** až po prokázání hodnoty ve výrobě; vyžaduje jinou znalostní vrstvu a citlivější data.

Agentní jádro první verze stačí zúžit na čtyři až pět funkcí: Framer, Diagnostician (A3 logika), Evidence Retriever, Solution Designer s kvantifikací a Red Team spolu se Synthesizerem.

### 18.3 Nasazení: jedno jádro, dva obaly

Desktop při vývoji a server při integraci lze obhájit jedním návrhem:

- **Core jako headless služba** (API, workflow engine, znalostní vrstva). Desktop aplikace je obal kolem UI a lokálně spuštěného core, serverová verze je stejné core v jiném balení.
- **Úložiště přes abstraktní vrstvu:** SQLite s vektorovým rozšířením pro desktop, PostgreSQL s pgvector pro server; stejný datový model a migrace.
- **Háčky pro server hned od začátku:** `tenant_id` v datovém modelu, auditní log, konfigurace oddělená od kódu. SSO, role a certifikace se odkládají do doby prvního korporátního zájemce.

### 18.4 Zákazník: design partner místo segmentu

Volba „střední firma nebo korporát podle zájmu" je rozumná, ale pro jednoho vývojáře doporučuji konkrétního **design partnera**: jednu výrobní firmu s A3 kulturou, která dodá reálné případy, zpětnou vazbu a pilot. Střední firmy jsou pro první rok vhodnější (kratší rozhodování, lokální nasazení, menší bezpečnostní zátěž). Korporát je cíl druhé fáze.

### 18.5 Vícejazyčnost: EN jako kanonický jazyk

Pořadí EN → CS → ES je správné a snižuje riziko:

- **Znalostní báze kanonicky v angličtině** + lokalizovaný pohled (názvy, shrnutí) a terminologický slovník lean pojmů (kaizen, muda, A3 a jejich překlady).
- **Multijazyčný embedding model** a testy retrievalu napříč jazyky (dotaz česky, zdroj anglicky).
- **Prompty a vnitřní uvažování v angličtině**, výstup generovaný nebo překládaný do jazyka uživatele jako samostatný krok s kontrolou terminologie.
- **UI s internacionalizací od prvního dne** (texty mimo kód).
- **Evaluační sada po jazycích:** zlaté případy pro každý jazyk, samostatný práh kvality.
- Nasazení: EN v MVP, čeština do pilotu, španělština až po prokázání hodnoty nebo podle zákazníka.

### 18.6 Kurátor: role, která se dá postavit i bez nalezeného člověka

Na začátku je kurátorem vývojář, ale tak, aby to nebylo úzké hrdlo:

- **Kurace podle rizika:** automaticky se publikuje jen záznam, který splní schéma, má dobrý původ a nízký dopad; ostatní jde do fronty. Cíl: fronta zvládnutelná v jednotkách hodin týdně.
- **Ověření odborníkem z praxe:** lean praktik (design partner nebo externí) validuje klíčové vzory a první desítky záznamů; ideálně autoři původních A3.
- **Zákazník kuruje vlastní vrstvu:** u interních případů výsledky potvrzuje sám jako součást učící smyčky.

### 18.7 Autonomie jako politika, ne jedno číslo

Odpověď, že autonomie záleží na komplexitě, datech a zkušenostech, je přesně správná a dá se zapsat jako konfigurovatelná politika:

- **Úroveň autonomie se počítá z podmínek:** úplnost dat, stupeň evidence, výsledek verifikace, shoda agentů, dopad (finanční, nevratnost) a **zkušenost** = naměřená přesnost daného typu kroku z učící smyčky.
- **Brány pro člověka se spouští pravidly:** nízká úplnost dat, doporučení P1 bez evidence stupně B a vyššího, nevyřešený rozpor mezi agenty, dopad nad prahem nastaveným klientem.
- **Start konzervativně (L0–L1)**; autonomie roste pro konkrétní typy kroků až podle dat z evaluace.

### 18.8 Realistická roadmapa pro jednoho vývojáře do 12 měsíců

Původní fáze počítaly s větším týmem. Při jednom vývojáři a kolísající dostupnosti je nutné odložit vše, co nepotvrzuje jádro hodnoty, a nechat rezervu.

1. **Měsíc 1 – validace:** zlaté A3 případy, prototyp řetězu promptů, ablace proti jednomu promptu, test lokálních modelů v EN a CS.
2. **Měsíce 2–3 – walking skeleton:** core služba, workflow s checkpointy, ledger, kontrakty agentů, 3 agenti, validace schémat a **evaluační harness hned zde**.
3. **Měsíce 4–6 – znalostní jádro:** schéma FaceModelu, A3 ingestion s anonymizací, 30–50 kurátorovaných záznamů, hybridní retrieval, verifikační vrstva.
4. **Měsíce 7–8 – kvantifikace a Red Team:** minimální Quant Engine (ROI, citlivost, základní Monte Carlo), graf předpokladů s přepočtem dotčených větví.
5. **Měsíce 9–10 – automatizace a zpevnění:** kurační fronty, základní učící smyčka, provozní telemetrie, zálohy, bezpečnostní kontrola.
6. **Měsíce 11–12 – pilot a rezerva:** pilot s design partnerem; rezerva zhruba 20–25 % celkového času na zpoždění.

**Odložit za rok 1:** datové konektory a ERP, monitorovací případy a Firemní rentgen, multi-tenant a SSO, španělština, FaceModel packs, plná vizuální simulační dílna, HR a finance jako samostatní agenti.

### 18.9 Co zůstává otevřené

1. **Hardware:** vývojový stroj je znám (kapitola 18.10); zbývá ověřit hardware pro první serverové nasazení u zákazníka.
2. **Design partner:** konkrétní výrobní firma pro pilot a zdroj reálných A3 případů.
3. **Vlastnictví a důvěrnost A3 dat** a způsob anonymizace.
4. **Kurátor nebo odborný validátor** z lean praxe.

### 18.10 Hardware vývojového stroje a jeho dopad na architekturu

Vývojový stroj: Ryzen 7 5800X, GPU s 16 GB VRAM (uvedeno RTX 5600 Ti; předpokládám RTX 5060 Ti 16 GB), 32 GB RAM. Je to dostatečné pro celý MVP, ale s jasnými limity.

- **Praktický strop je třída modelů kolem 14 B v kvantizaci Q4** (zhruba 9–10 GB VRAM) s kontextem do \~16–32 tis. tokenů. Větší modely (24–32 B) se buď vejdou jen těsně s malým kontextem, nebo přetečou do RAM a zpomalí.
- **Jeden velký model najednou.** Agenti proto běží sekvenčně; paralelismus je výjimka, ne základ. Malý embedding model (do \~1–2 GB) se vejde vedle hlavního modelu.
- **Dvojí běh s druhým modelem** (diverzita u kritických kroků) znamená přepnutí modelu; s 32 GB RAM je přepnutí rychlé, ale není zadarmo. Počítá se s ním v rozpočtu času.
- **Orientační doba případu:** jednotky až nízké desítky minut pro standardní režim. Přesná čísla dá až měření ve Fázi 0. Režim Rychlý (3 agenti) má být v řádu minut.
- **Kvalita:** na tomto strojích je realistická angličtina i strukturovaný výstup; čeština a španělština budou slabší než angličtina. Potvrzuje to volbu EN jako kanonického jazyka a evaluaci po jazycích.
- **Strategie modelů:** malý model (4–8 B) pro klasifikaci a extrakci, 14B třída pro uvažování a syntézu, vše za Model Routerem jako konfigurace. Kandidáty ve Fázi 0 vybrat podle aktuální nabídky v Ollamě; testovat i MoE modely, které na 16 GB mohou dát lepší poměr kvalita/rychlost.
- **Referenční model pro hodnocení:** ve Fázi 0 porovnat výstupy na anonymizovaných zlatých případech s výkonnějším (i cloudovým) modelem jen jako měřítko stropu kvality lokálních modelů. Důvěrná data tam nepatří.
- **Server u zákazníka** bude mít jiný hardware (typicky víc VRAM): model je proto vždy konfigurace, nikdy předpoklad v kódu.
