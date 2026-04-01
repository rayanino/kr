# Onderzoek naar ontwerp van een ochtendrapport voor een autonome overnight quality factory

## Wat de huidige baseline precies rapporteert

De huidige `generate_morning_report()` in `scripts/overnight_orchestrator.py` is primair **task-gericht** (wat is er met taken gebeurd) en pas in tweede instantie **finding-gericht** (welke issues zijn gevonden), met één compacte aggregatiesectie op het einde. fileciteturn4file0L1-L1

Concreet is de informatiestroom vandaag:

- Het rapport opent met een titel op basis van `state.run_id` (bij jullie format: datumstring) en gaat daarna meteen naar een “Summary” met looptijd, taak-tellingen (completed/failed/skipped/rolled_back), status, kosten en een git-range (start-hash → actuele `HEAD`). fileciteturn4file0L1-L1  
- Daarna volgt “Completed Tasks”, gegroepeerd per `category`, met per item duur, model en (indien >0) kosten. fileciteturn4file0L1-L1  
- Falen/timeout/rollback verschijnen als een “Issues (YOUR ATTENTION NEEDED)” lijst, maar zonder onderscheid tussen **infrastructuurproblemen**, **kwaliteitsgate failures** en “inhoudelijke” regressies (alles zit in één bucket). fileciteturn4file0L1-L1  
- Er is een “Review First” sectie die enkel werkt voor taken met `category == "review"` en een `review.md` outputbestand. fileciteturn4file0L1-L1  
- Pas daarna wordt `overnight/results/<task_id>/findings.json` geaggregeerd naar “Findings Summary”. Die sectie telt bugs per severity en geeft detailregels voor **CRITICAL + HIGH** bugs (met fixed/unfixed), een telling tests toegevoegd (met “net delta”), spec-issues en learnings. fileciteturn4file0L1-L1  
- Tot slot wordt `overnight/decisions.log` als een lijst met timestamped entries opgenomen (“Autonomous Decisions Made”). fileciteturn4file0L1-L1  

Wat deze baseline goed doet (als “v2-harnas”): hij is robuust (atomische writes), hij linkt naar concrete artefacten op disk (`results/…`), en hij heeft een audit trail via `decisions.log`. Dit komt ook expliciet terug in de `overnight/README.md` beschrijving van de architectuur en de ochtend-review flow. fileciteturn8file0L1-L1

Maar: als je dit wil opschalen naar een **autonome factory** die maanden draait, is dit huidige rapport (a) te weinig **actie-oriëntatie** aan de top, (b) te weinig **run-over-run geheugen** (trends/MTTR), en (c) nog niet ontworpen rond **routing / escalatie / shadow routing** die je in de hardening-beslissingen beschrijft. fileciteturn3file0L1-L1

## Wat je DRAFT-ontwerp beoogt en welke eisen het impliciet introduceert

In `reference/FACTORY_HARDENING_DECISIONS.md` positioneer je het ochtendrapport als “primary interface” tussen factory en architect. Je DRAFT zet vier eisen centraal: CRITICAL bovenaan, zichtbaarheid van de vier-tool routing, expliciete escalatie-tracking, en shadow-routing resultaten; plus een JSON-intermediate voor latere dashboards. fileciteturn3file0L1-L1

Belangrijk is dat dit rapport-ontwerp niet op zichzelf staat: het leunt op de rest van je beslissingen rond routing en veiligheid:

- **Vier-tool routing** (rollen per tool/provider) betekent dat het rapport een audit trail moet kunnen tonen van “welke tool, welk model, waar ingezet”. fileciteturn3file0L1-L1  
- **Deterministische severity-classificatie** betekent dat het rapport niet alleen “severity” toont, maar ook (idealiter) de deterministische rule/trigger die tot die severity leidde. fileciteturn3file0L1-L1  
- **Escalatiepaden** (pre-scan en mid-review interrupt) betekenen dat je een “finding lifecycle” krijgt: initieel laag → opgewaardeerd → hergerouteerd → (eventueel) scope-pause. fileciteturn3file0L1-L1  
- **Shadow routing** introduceert een tweede “waarheid”: een steekproef die bedoeld is om blind spots te detecteren; daarvoor heb je vergelijking, labeling en trenddetectie nodig. fileciteturn3file0L1-L1  

Het gevolg: je DRAFT verplaatst het ochtendrapport van “samenvatting van tasks” naar “samenvatting van *operational control*”: waar moet de architect *ingrijpen*, en waar toont de factory *bewijs* dat het systeem zichzelf betrouwbaar monitort.

## Patronen uit productie CI/CD, build-sheriffing, canary analyse en MLOps rapportage

Er bestaan meerdere “families” van dagelijkse/overnight rapportering in productieomgevingen. Ze hebben verschillende vormen (dashboards, chatops-notificaties, PDF/HTML summaries), maar ze convergeren opvallend sterk op een paar ontwerpprincipes: **actie eerst, bewijs daarna; baseline-vergelijking; en aandacht voor ruis (noise) vs signaal.**

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Chromium buildbot waterfall console screenshot","Jenkins build dashboard build history screenshot","Spinnaker canary analysis stage screenshot","MLflow tracking UI runs screenshot"],"num_per_query":1}

### Build sheriff / build cop: dagelijkse triage- en herstelpraktijk

In grote CI-systemen is er vaak een expliciete on-call rol (build sheriff/build cop) met één kernmissie: **de “tree” open en gezond houden**, en regressies snel isoleren en terugdraaien. In de Chromium sheriffing-gids is de prioriteit expliciet: tree open houden, voorkomen dat nieuwe failures binnenkomen, en bestaande failures repareren; sheriffs hebben ook expliciet mandaat om reverts te doen of tests te disablen. citeturn2search3

De Drake build-cop procesbeschrijving is nog concreter: notificatie bij CI failures, triage naar culprit commits vs infra-issue, en snelle revert als auteurs niet tijdig reageren; flaky/intermittent failures worden als issues gelogd en beheerd; en er is een duidelijke rotatie/hand-off. citeturn2search0

Wat dit betekent voor jouw ochtendrapportontwerp:

- “**Wat is gebroken / wat bedreigt het systeem**” moet in één oogopslag zichtbaar zijn (equivalent van tree-open/closed). citeturn2search3turn2search0  
- Er hoort bijna altijd een onderscheid te bestaan tussen **code-regressie**, **CI-infrastructuur**, en **flaky instabiliteit**, omdat het “remediation pad” anders is (revert/fix-forward vs infra escalate vs quarantine/flake-tracking). citeturn2search0  

### Canary analyse: baseline vs canary, met drempels en “kritieke metrics”

Canary-rapporten in progressive delivery zijn per definitie **vergelijkingsrapporten**: een canary wordt beoordeeld tegenover een baseline, met drempels voor pass/marginal/fail en met het concept van “kritieke” metrics die onmiddellijk falen kunnen triggeren. De Spinnaker canary best practices benadrukken expliciet: vergelijk tegen een equivalente baseline, wees voorzichtig met metric-groepering, en gebruik duidelijke thresholds (marginal/pass) die je iteratief bijstelt. citeturn6search0  
De uitleg van hoe de “judge” werkt beschrijft bovendien heel concreet hoe scorevorming, no-data regels en “critical metric failure” in beslissingen doorwerkt. citeturn6search2  

De analogie naar jouw factory is nuttig: een ochtendrapport dat alleen absolute aantallen toont (“8 MEDIUM gevonden”) mist vaak de kernvraag: **is dit beter/slechter dan gisteren**, en **welke signalen zijn ‘critical’ genoeg om een automatische pause/escalatie te rechtvaardigen**. citeturn6search0turn6search2  

### SRE/observability: “symptomen vs oorzaken” en actiegerichte signalen

In operationele rapportage (niet alleen alerts) is een klassieke valkuil: te veel “oorzaak-hypotheses” bovenaan, en te weinig “symptoom/impact” of omgekeerd. Het Google SRE-boek benadrukt het onderscheid “wat is er stuk?” versus “waarom?”, en dat dit cruciaal is voor hoge signaal/lage ruis monitoring. citeturn2search6  

Ook SRE guidance rond alerting-on-SLOs legt een sterk accent op **actiegerichtheid**: je wil notificaties (of ‘top-of-report’ items) die correleren met betekenisvolle budget/risico-consumptie, en je wil vermijden dat je systeem te vaak “schreeuwt” voor niet-significante events. citeturn7search0  
Voor jouw ochtendrapport vertaalt dit naar: bovenaan should staan wat *nu actie vereist*, en lager in het rapport hoort het “bewijs” te staan waarmee je die actie prioriteert.

### MLOps monitoring: periodieke runs, baseline constraints, violations en metadata stores

MLOps monitoring rapporten zijn vrijwel altijd: **(1) scheduled** (periodiek), **(2) baseline-gedreven** (trainingsbaseline / constraint set), en **(3) violation-gedreven** (wat wijkt af). Bijvoorbeeld: entity["company","Amazon","technology company"] SageMaker Model Monitor beschrijft expliciet hoe monitoring jobs op schema draaien, een baseline (statistics + constraints) bouwen, en dan latere data vergelijken met die constraints en violations rapporteren. citeturn5search0turn5search1  
In het drift-voorbeeld wordt zelfs een expliciete “violations” JSON-structuur getoond (feature_name, constraint_check_type, etc.). citeturn5search4  

Dat is een sterk precedent voor jouw systeem: je “nightly factory” is eigenlijk een periodieke kwaliteitsmonitor. Als je de report-architectuur ontwerpt alsof het een MLOps monitor is, kom je bijna vanzelf uit op: baseline vergelijken (vorige nacht als “baseline”), expliciete violations (findings), en een metadata-historiek (store) om trends te kunnen berekenen. citeturn5search0turn5search4  

### Academische en industrie-onderzoekslijnen die rapportbehoeften beïnvloeden

Er is veel onderzoek naar CI-efficiëntie en betrouwbaarheid dat indirect vertelt **welke dimensies teams willen monitoren**:

- Build failures worden actief gemodelleerd/predicted (kosten en triage-schaal); dat impliceert dat teams build metadata en failure signals systematisch opslaan, niet ad-hoc. citeturn4search1turn4search2  
- Test flakiness is een erkend productiviteits- en release-risico; studies en reviews benadrukken dat flaky tests CI verstoren en dat reruns/ML-detectie frequent voorkomen. Dit wijst erop dat “flaky vs deterministic” in rapportage en triage echt een eerste-orde categorie is, niet een detail. citeturn4search3turn4search4  

Voor jouw ochtendrapport is de praktische les: als je niet expliciet “flaky / intermittent / infra” labelt, kun je (zeker na weken) niet meer onderscheiden wat *echte regressie* is versus *systeemruis*.

## Gap-analyse van de informatiehiërarchie

Hier vergelijk ik: (a) baseline `generate_morning_report()`; (b) jouw DRAFT; en (c) wat productiepatronen typisch toevoegen. De DRAFT is duidelijk een stap vooruit; er zijn wel een paar hiaten die in productie vrijwel altijd opduiken zodra de rapporten weken/maanden gebruikt worden.

### Trend- en baselinevergelijking ontbreekt als primair signaal

Je DRAFT noemt (impliciet) geen “verschil t.o.v. vorige run” als vaste top-structuur. Maar in canary analyse en monitoring is dat net de kern: *deviation from baseline*. citeturn6search0turn5search0  

Praktisch voorstel: laat in “Summary” niet alleen absolute waarden zien, maar ook **Δ vs vorige nacht** voor:

- #findings per severity  
- #escalaties en #shadow disagreements  
- totale duur en gemiddelde task latency per tool  
- kosten (en burn rate als je quota/cost-cap toevoegt)  

Dit hoeft geen grote time-series te worden; één regel “Δ vs gister” levert al een enorme cognitieve winst op.

### Actie-items en eigenaarsschap moeten explicieter

Build-sheriffing documentatie maakt zichtbaar dat de cruciale output van CI triage niet “wat gebeurde” is, maar “wie doet wat nu” (revert, file issue, disable test, ping owner). citeturn2search3turn2search0  

Je DRAFT heeft een “🚨 CRITICAL” sectie, maar ik mis als expliciete top-node:

- een **Action Queue** die *alleen* items bevat die een mens moet doen (architect review, unpause scope, approve fix, etc.);  
- en per item: (i) suggestie van “owner”/responsible (kan initieel de architect zijn), (ii) concrete next step, (iii) link naar artefact (diff, log, test).  

Zonder die scheiding ga je (zeker als het rapport groeit) dezelfde valkuil krijgen als noisy alerting: de lezer krijgt veel informatie maar weinig expliciete “to do”. Dit sluit aan bij SRE-advies om vooral actiegerichte signalen te creëren. citeturn7search0turn2search6  

### Time-to-resolution en build-health metrics zijn afwezig

In CI tooling zie je vaak metrics zoals **MTTF/MTTR** omdat het een directe maat is voor “build health” en operationele discipline. Zelfs in de Jenkins-ecosystemen bestaan plugins die expliciet MTTF/MTTR over vensters (7d/30d/all-time) tonen. citeturn1search1  

Voor jouw factory zijn er twee MTTR’s die nuttig zijn:

- **MTTR voor “findings”**: tijd van first_seen → resolved (of “fixed+validated”).  
- **MTTR voor “runs”/pipeline gezondheid**: hoe lang duurde een periode met CRITICALs, of met structurele failures (bijv. quality gate rollbacks) voordat het terug “green” is.

Je huidige baseline kan dit niet omdat (1) er geen stabiele finding-ID over runs bestaat en (2) oude run-state wordt opgeschoond bij start. fileciteturn4file0L1-L1  

### Clean-night fast path ontbreekt als UX-anker

In de praktijk is de meeste waarde van een dagelijks rapport: **snel weten dat je niets hoeft te doen**. Canary- en monitoring-systemen hebben typisch een “PASS” state die één regel kan zijn. citeturn6search2turn5search0  

Je DRAFT zegt: “CRITICAL sectie verschijnt alleen wanneer CRITICALs bestaan” — goed — maar ik zou expliciet een “All clear” top-blok toevoegen wanneer:

- geen CRITICAL/HIGH  
- geen escalaties  
- geen shadow disagreements  
- geen task failures/rollbacks  

Dat blok is niet alleen cosmetisch: het vermindert cognitieve belasting en voorkomt dat de rapportlezer steeds het hele document moet scannen om zekerheid te krijgen.

### Rapport-archivering en artefact-retentie zijn nog onderschat

Productiesystemen behandelen run-outputs als **artefacten** met retentie/traceability. entity["company","GitHub","code hosting company"] Actions documentatie benadrukt dat artifacts bedoeld zijn om build/test output te bewaren na afloop van een run (logs, test results, coverage, dumps) en dat je retentie kan configureren. citeturn1search0turn1search3  

Jouw orchestrator bewaart wel `overnight/results/<task_id>/…`, maar het model “we verwijderen state van vorige runs bij start” maakt het lastig om maandenlang historiek op te bouwen zonder extra archiefstructuur. fileciteturn4file0L1-L1  
Als je straks trends, MTTR, en “recurring finding” wil, is run-archief de fundering.

### De DRAFT mist expliciete “difference report / changed surface area”

CI best practices noemen vaak expliciet dat builds een **difference report** en/of BOM-achtig overzicht moeten kunnen geven (“wat veranderde t.o.v. vorige build”). citeturn0search1  
Je DRAFT toont git-range, maar ik zou toevoegen:

- lijst gewijzigde bestanden (top N)  
- #commits en commit-messages in die range (of enkel “overnight:” commits)  
- mapping van findings → gewijzigde bestanden / commits (waar mogelijk)

Dit is met name nuttig wanneer de factory autonoom fixes commit: dan is het ochtendrapport ook een “release note” voor de architect.

## CRITICAL dubbel tonen zonder redundantie of verwarring

Je vraag is precies juist: CRITICALs zowel bovenaan als in “Findings by Severity → CRITICAL” kan redundant worden. In productie zie je meestal één van deze patronen:

### Patroon met progressieve disclosure

1. **Bovenaan**: een actie-gedreven CRITICAL samenvatting (max 5–10 regels) met alleen:
   - ID + korte omschrijving  
   - reden waarom het CRITICAL is (rule/affected fields)  
   - status (paused? fixed? needs review?)  
   - “Next action” (review/approve/unpause)  
2. **Later**: een volledige “Findings log” waar CRITICAL opnieuw verschijnt, maar als **complete record** (alle velden, tooloutputs, links).  

Dit is niet echt duplicatie, zolang het topblok een ander doel dient (triage) dan het logblok (audit trail). Dit sluit aan bij SRE “symptoom eerst, oorzaak later” denken, en bij canary rapporten waar je eerst de “judgment” ziet en daarna de metric-detail. citeturn2search6turn6search2  

### Patroon met expliciete verwijzing in plaats van herhaling

Als je echt wil vermijden dat CRITICAL twee keer “vol” verschijnt, kun je:

- Topsectie: lijst CRITICALs met korte omschrijving.  
- In “Findings by Severity”: toon alleen `CRITICAL (N) — zie sectie bovenaan` en laat CRITICAL entries daar weg, maar behoud HIGH/MEDIUM/LOW detail.  

Dit vermindert scroll-lengte, maar verliest een consistent “alle severities hebben dezelfde detailstructuur” in één sectie.

### Praktische implementatietip voor Markdown

Als je het rapport vaak in een renderer bekijkt die HTML tags ondersteunt (zoals entity["company","GitLab","devops company"] / entity["company","GitHub","code hosting company"] Markdown viewers), is `<details>` een bewezen patroon: topsectie blijft compact, detailsectie kan openklappen per finding of severity. Ook GitHub job summaries ondersteunen expliciet samengestelde Markdown en hebben harde size limits per step; dat is nog een reden om collapsible detail te overwegen zodra je output groeit. citeturn7search1  

## Is report_data.json het juiste intermediate format voor maandenlange runs

### Wat productieplatformen doen met run-metadata

In MLOps is het heel normaal om run-metadata niet alleen als files te bewaren, maar in een **metadata store** (vaak een database) zodat je makkelijk lineage, trends en queries doet:

- entity["company","Google","technology company"] TFX ML Metadata (MLMD) beschrijft expliciet een “Metadata Store” (database) die artefacten en executions registreert, met referentie-implementaties o.a. voor SQLite. citeturn3search4  
- Kubeflow Pipelines beschrijft dat de backend runtime info (task status, artifacts, properties) opslaat in een metadata store en lineage graphs ondersteunt; het is dus ontworpen rond “queryable history”. citeturn3search1  
- MLflow documenteert een backend store voor run-metadata en benoemt dat een relationele database betere performance/scale geeft via indexing; file-based backends bestaan, maar worden als “legacy/deprecated soon” gepositioneerd. citeturn3search3turn3search2  

Deze bronnen zijn niet “CI reports” per se, maar ze zijn wél exact jouw probleem: een periodiek systeem dat maanden draait en waar je achteraf vragen wil kunnen stellen als “wat is er veranderd?”, “wat was de trend?”, “wat is recurring?”, “wat was MTTR?”. citeturn3search4turn3search3  

### Evaluatie van JSON als intermediate

**Structured JSON (`report_data.json`) per run** is een goede keuze als:

- je een duidelijke scheiding wil tussen **data-aggregatie** en **rendering** (Markdown/HTML later)  
- je portability wil (later dashboards, scripts, jq/pandas)  
- je beperkte schaal verwacht (1 file per nacht, enkele MB)

Maar JSON-per-run alleen heeft een aantal typische opschaalproblemen na weken/maanden:

- trendberekening wordt “scan alle oude JSON files” (traag en foutgevoelig)  
- crash recovery / partial writes zijn lastiger als één JSON blob “de waarheid” is  
- schema evolutie (versies) is moeilijker zonder migratie-/compatlaag

### Een hybride patroon dat goed past bij jouw factory

Gezien je al een append-only `decisions.log` hebt (en dus al event-achtig denkt), zou ik voor maandenlange runs een **twee-laags** model adviseren:

1. **Append-only event ledger (JSONL)**  
   - Eén regel per event: `task_started`, `task_finished`, `finding_detected`, `review_completed`, `escalated`, `shadow_compared`, `scope_paused`, `quota_sampled`, …  
   - Voordelen: incrementeel, weinig corruptierisico, makkelijk te tailen, ideaal voor audit.

2. **Materialized snapshot per run (report_data.json + MORNING_REPORT.md)**  
   - Aan het einde van de run maak je één “gesloten” snapshot die het ochtendrapport reproduceerbaar maakt.

Daarbovenop kun je optioneel een **SQLite** file hebben als “query cache”. Dat is exact wat MLMD/MLflow normaliseren: SQLite is laagdrempelig (één bestand), maar wél indexeerbaar en queryable. citeturn3search4turn3search3  

### Wanneer zou je wél naar event streams gaan?

Een echte event stream (Kafka/PubSub) wordt pas rationeel als:

- je meerdere consumers hebt (dashboards in real-time, alerting, incident automation)  
- je meerdere nodes hebt (distributie, concurrency)  
- je retentie/observability centraal wil beheren

Voor “één repo, één nacht-runner” is dat meestal overkill; het hybride JSONL + snapshot + (optioneel) SQLite patroon levert 80–90% van de voordelen met een fractie van de operationele last.

### Implicatie voor je DRAFT

Mijn advies zou dus niet zijn “JSON is fout”, maar: **`report_data.json` is een prima snapshot-format, maar niet voldoende als enige waarheid** wanneer je trenddata, MTTR en recurring-finding tracking serieus neemt. Gebruik JSON voor snapshots, en voeg een append-only ledger of DB toe voor historiek. citeturn3search3turn1search0