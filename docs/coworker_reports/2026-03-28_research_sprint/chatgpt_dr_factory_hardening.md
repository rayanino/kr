# Hardening van de KR Factory: onafhankelijke verificatiebronnen, rijal-seeding, Shamela cross-checks en evaluatie- en testmethoden

## Context uit de repo: wat je al hebt gebouwd en waar de gaten zitten

Je repo positioneert de “factory” als een pijplijn met expliciete data-contracten, vertrouwenlagen, en veldniveau‑confidence die upstream beslissingen downstream afdwingen. Dat is cruciaal, want de “hardening” die je vraagt is in de praktijk: **meer onafhankelijke ankers** toevoegen (niet-LLM bronnen + deterministische checks) en die ankers consistent laten “meespelen” met je bestaande gating/errortaxonomie.

De twee meest load‑bearing artefacten (voor deze research) zijn:  
- De **source engine contracts** met je canonieke schema’s (o.a. `SourceMetadata`, `ScholarAuthorityRecord`, enums voor `TrustTier`, `Genre`, `AttributionStatus`, error codes en cross-validation stubs). fileciteturn7file0L1-L1  
- Het feit dat `library/registries/scholars.json` nu leeg is (Finding 4) en dus elke “authority bootstrap” nog ontbreekt. fileciteturn6file0L1-L1  

In `SourceMetadata` trek je o.a. de volgende metadata‑velden uit bronnen: `title_arabic`, `author` (als `ScholarReference`), `attribution_status`, `muhaqiq`, `science_scope`, `genre`, `structural_format`, publicatievelden (`publisher`, jaren), multi-layer structuur (`is_multi_layer`, `text_layers`), plus een expliciet blok voor **confidence tracking** (`confidence_scores`, `needs_review_fields`) en trust‑/fidelity‑scores. fileciteturn7file0L1-L1  
In `ScholarAuthorityRecord` heb je al een ambitieus doelmodel voor rijal/tabaqāt‑achtige authoriteit: namen/varianten, geboorte/sterfte (Hijri + CE), `school_affiliations` per wetenschap, `sectarian_tradition`, `teachers`/`students`, `known_works`, provenance‑scores en zelfs een “cross validation” placeholder. fileciteturn7file0L1-L1  

Je excerpting engine spec bevat bovendien expliciete “consensus verification” (multi‑model verificatie) als deel van je kwaliteitsstrategie. fileciteturn5file0L1-L1  
De hardening‑vraag is dus: **welke extra, domeinspecifieke bronnen en methodes kun je aansluiten zodat “consensus” niet alleen LLM‑LMM is, maar ook LLM‑vs‑corpus/authority**?

## Wat je waarschijnlijk mist: concrete externe tools en databronnen die als onafhankelijke “anchors” kunnen dienen

Hieronder groepeer ik per verificatiebehoefte (author attribution, genre, madhhab, matn/sharh, decontextualisatie) alleen bronnen/tools die *zelf metadata leveren of strong signals geven*—dus bruikbaar als onafhankelijke check op LLM‑extracties.

### Author attribution en identiteitsdisambiguatie

**OpenITI author/book authority via YAML + CTS‑achtige URIs**  
OpenITI onderhoudt per auteur, werk en versie machine‑leesbare metadata in aparte YAML‑records (YML‑3 author record, YML‑2 book record), met een URI‑systeem waarin *authorID* standaard de (approx.) sterftejaar‑Hijri + šuhra encodeert, en author records ook teacher/student relaties kunnen bevatten. citeturn0search0turn4search7  
Dit is precies het soort “independent authority” dat je schema al verwacht (death dates, teachers/students, naamvarianten), en het is nuttig omdat het buiten je LLM‑extractie staat.

**Wikidata als redundante authority laag (SPARQL + property constraints)**  
Wikidata biedt een SPARQL endpoint en programmeerbare resultaten (JSON/XML/CSV) voor entity‑graphs. entity["organization","Wikidata","wikimedia knowledge base"] heeft expliciete properties voor:  
- *madhhab* (P9929): “Islamic school of thought within fiqh”. citeturn2search7  
- teacher/student relaties via “student of” (P1066) (inverse van “student” P802). citeturn2search8  
Omdat jij in `ScholarAuthorityRecord` teacher/student edges + temporal consistency rules hebt (bv. teacher death > student death + 30 jaar → inconsistency), is Wikidata een directe, structurele input voor jouw genealogie‑laag (met provenance). fileciteturn7file0L1-L1  

**Shamela master + author DB als onafhankelijke “bibliografische waarheid”**  
De `shamela` npm library (ragaeeb/shamela) geeft toegang tot Shamela v4 “master database” metadata (books/authors/categories) en per‑boek metadata via API calls (`getMaster`, `getBookMetadata`, `getBook`, `downloadMasterDatabase`, `downloadBook`). citeturn1search1turn1search0  
Voor author attribution is dit primair nuttig omdat Shamela’s eigen database vaak *author association + boek‑id + categorie* bevat, en je dat kunt vergelijken met je eigen intake‑extractie.

### Genre‑classificatie verificatie

**OpenITI YML‑2 “Book Record” met multi‑source genre tags**  
OpenITI’s YML‑2 kent een veld `10#BOOK#GENRES###` waarin genres/tekstvormen kunnen staan met herkomst (“src@keyword”, bv. een bibliografische bron zoals GAL). citeturn4search7  
Dat is waardevol omdat het expliciet een *bronlabel* draagt: je kunt genre‑conflicten detecteren (LLM zegt “sharh”, OpenITI zegt “hadith”/“fiqh” etc.) en die conflicts in jouw `needs_review_fields` of human gate triggers duwen. fileciteturn7file0L1-L1  

**Shamela categories (discipline/genre‑achtig) als tweede opinie**  
De master dataset die `shamela` kan ophalen bevat `categories` naast `books` en `authors`. citeturn1search1  
Shamela’s categorieboom is niet “academisch neutraal”, maar precies daarom bruikbaar als check: als jouw pipeline een genre toekent dat totaal buiten Shamela’s classificatie ligt, is dat een sterke outlier‑indicator.

### Madhhab / school-of-thought identificatie

**Wikidata “madhhab” (P9929) + SPARQL queries**  
Omdat madhhab een first‑class Wikidata property is, kun je author‑nodes verrijken met (a) madhhab, (b) teacher/student, (c) death date, en dit mechanisch als provenance‑bron in je `school_affiliations` en/of `sectarian_tradition` opnemen. citeturn2search7turn2search0  
Dit past bij je schema‑intentie om sectarian/tradition mismatches te voorkomen (“prevents silent mixing of traditions”). fileciteturn7file0L1-L1  

**Belangrijke nuance voor verificatie**  
Wikidata is crowd‑sourced; je wil het dus zelden als “single source of truth”, maar wel als **triangulatiebron** in je cross-validation model (die je al in contracts hebt uitgetekend: `DeathDateAgreement`, `KnownWorksUnion`, `WikidataTeacherStudentLinks`). fileciteturn7file0L1-L1  

### Matn/sharh (en bredere structurele lagen) detectie

**KITAB passim text‑reuse als structurele “evidence layer”**  
KITAB beschrijft text reuse detection met passim specifiek als methode om o.a. te onderzoeken “hoe een commentary op een werk gestructureerd is, en hoe ver het herschikt of afwijkt van het origineel”. citeturn4search0  
Technisch relevant voor jou: KITAB chunked OpenITI teksten in *milestones* (300 woorden) en gebruikt Smith‑Waterman alignments om hergebruikte passages te vinden. citeturn4search0  
Dit is een directe, externe manier om te toetsen of:  
- een vermeende sharh substantieel reuse/quoting vertoont van een base matn;  
- een “matn‑quote” in je excerpt eigenlijk een overgenomen fragment is uit een ander werk.

**OpenITI mARkdown parsing/TEI conversion tooling**  
OpenITI mARkdown is ontworpen als lichtgewicht annotatie/markup voor RTL teksten; er bestaan Python tools om mARkdown te parsen (`oimdp`) en naar TEI te converteren (`oitei`). citeturn4search6turn4search12turn4search4  
Voor jouw use case: als je je eigen normalisatie/structuurdetectie wil verifiëren, is “mARkdown→parsed structure” een onafhankelijke parser‑baseline waarmee je kunt checken of je headings/sections consistent worden herkend, en of excerpt‑grenzen op zinvolle structurale grenzen vallen.

**Shamela content utilities als praktische structure parser voor Shamela HTML**  
De `shamela` library bevat content tooling zoals `parseContentRobust`, `sanitizePageContent`, `splitPageBodyFromFooter`, en helpers om Shamela‑specifieke tags/markers te normaliseren. citeturn1search1  
Dit is nuttig als je (a) je eigen Shamela HTML normalisatie wil verifiëren, en (b) structurele segments (hoofdstuktitels/TOC, voetnoten vs body) wil losmaken voordat je LLM excerpting doet.

### Decontextualisatie-detectie (excerpt is losgetrokken van wat het weerlegt)

Er bestaat zelden een kant‑en‑klaar “decontextualization detector” voor klassieke Arabische polemiek, maar je kunt wel externe signals combineren zodat *loss of refutation context* detecteerbaar wordt.

**Text reuse + alignment als “context‑verankering”**  
Als je excerpt vermoedelijk een weerlegging bevat maar niet de stelling, dan zie je vaak:  
- markers of citaten die elders in corpus terugkomen (bijvoorbeeld de aangehaalde positie wordt letterlijk geciteerd),  
- en/of hergebruikspatronen die op quotations wijzen.  
KITAB’s passim/alignments zijn precies bedoeld om gedeelde passages tussen werken te vinden en te visualiseren. citeturn4search0turn4search3  
Een praktische verificatie‑strategie is: *zoek in reuse‑alignments of je excerpt begint midden in een alignment zonder de “introductie” (argument setup) mee te nemen*.

**Automatische Qurʾan‑detectie als precedent voor “boundary problems”**  
KITAB heeft expliciet een project om Qurʾan‑citaten in de OpenITI corpus automatisch te taggen, inclusief het bepalen van sūra/āya en het moeilijkste deel: *waar eindigt “Qurʾan‑taal” en waar begint “citaat”*. citeturn4search1  
Dat is methodologisch relevant: jouw decontextualisatie‑probleem is ook een boundary‑probleem. Je kunt dezelfde evaluatie‑logica hergebruiken: (a) definieer boundary rules, (b) maak gold annotations voor een gestratificeerde sample, (c) meet boundary error types, (d) verbeter heuristiek/model.

## Rijal/tabaqāt data: concrete datasets/APIs voorbij usul-data om `scholars.json` te vullen

Je `ScholarAuthorityRecord` vraagt expliciet om sterfte‑data, school‑affiliaties, teacher/student edges en known works. fileciteturn7file0L1-L1 Je wilt dus bronnen die minstens één van die assen structureel leveren.

### OpenITI author records als basis “tabaqāt‑achtig” skelet

OpenITI’s YML‑3 author records beschrijven auteurs met naamcomponenten (ism/kunya/laqab/nisba/shuhra), geboorte/sterfte in AH, en kunnen `40#AUTH#STUDENTS#` en `40#AUTH#TEACHERS#` bevatten (OpenITI author URIs). citeturn0search0  
Dit is één van de weinige grootschalige, academische corpora waar teacher/student al onderdeel van het datamodel is; ideaal om jouw genealogy‑velden te seeden.

### Wikidata voor (madhhab + genealogie + dates) via SPARQL

Wikidata’s SPARQL service is ontworpen voor exactly deze taak: gestructureerde graph‑extractie op properties (dates, relaties). citeturn2search0  
Voor rijal‑achtige verrijking zijn de twee kernproperties die je nu al hard kunt inzetten:  
- madhhab (P9929) citeturn2search7  
- student of (P1066) / student (P802) (teacher‑student edge) citeturn2search8  

Omdat jij al cross-validation structuren in je contracts hebt staan om Wikidata als bron te integreren, kun je dit snel omzetten in een “authority bootstrap job” die (1) een seed‑lijst van scholars maakt en (2) provenance‑labels zet per veld. fileciteturn7file0L1-L1  

### Shamela narrators export: “rijal‑dataset” die je waarschijnlijk nog niet had gecatalogeerd

Een opvallende vondst: de `shamela` tooling documenteert scripts die uit Shamela desktop databases exporteren, waaronder: **“Exports 18,989 narrator biographies from S1.db”**. citeturn1search1  
Dat is extreem relevant voor jouw rijal‑behoefte, omdat het een kant‑en‑klare, gestructureerde narratorenlijst suggereert (met biografie‑velden afhankelijk van wat S1.db bevat). Dit is niet hetzelfde als alle “scholars” (fuqahāʾ, muḥaqqiqūn), maar voor hadith‑ketens is het een directe authority bron.

### Praktisch seeding-model dat aansluit op jouw contracts

Je contracts geven al consistency rules voor scholar updates (drift‑detectie, school conflict, teacher/student temporal checks). fileciteturn7file0L1-L1  
Een realistische bootstrapping‑volgorde die je provenance‑scores snel omhoog brengt:

1. **Seed set A (OpenITI)**: maak `canonical_id` records voor alle OpenITI auteurs die je collectie raakt, inclusief `death_date_hijri`, basis naamvelden en teacher/student URIs waar beschikbaar. citeturn0search0  
2. **Seed set B (Shamela)**: importeer (a) narratoren uit S1.db export als aparte categorie (bv. `sectarian_tradition` + domain tag “hadith_narrator”), (b) authors uit master DB als bibliografische uitlijningsbron. citeturn1search1  
3. **Cross‑validate (Wikidata)**: query per scholar op naamvarianten + death date; vul madhhab (P9929) waar beschikbaar; haal teacher/student edges (P1066/P802) als extra graph edges. citeturn2search7turn2search8turn2search0  
4. Schrijf `cross_validation` terug wanneer je dat stuk implementeert (je data‑modellen voorzien het al). fileciteturn7file0L1-L1  

## Shamela cross-referencing: hoe `ragaeeb/shamela` specifiek bruikbaar is voor jouw `SourceMetadata` verificatie

De shamela npm library is niet alleen “download een boek”; het is een volledige lifecycle abstraction: master metadata ophalen/downloaden, book metadata ophalen, book content ophalen, en bovendien content‑normalisatietools voor Shamela formatting. citeturn1search1turn1search0  

### Waarom dit past op jouw `SourceMetadata` contract

Je contract voorziet expliciet `source_format = SHAMELA_HTML` en een `format_specific_metadata` dict met als voorbeeld `shamela_book_id` en `shamela_category`. fileciteturn7file0L1-L1  
Dat betekent dat je al een plek hebt om Shamela‑IDs en categorieën in je metadata‑keten te bewaren—zodat verificatie downstream reproduceerbaar is (“dit boek was Shamela id X op master versie Y”).

### Crosswalk: Shamela API velden naar jouw velden

Onderstaande mapping is wat je typisch kunt implementeren als “verificatie‑enrichment” stap nadat je intake LLM‑extractie klaar is.

| Jouw veld (SourceMetadata / ScholarAuthority) | Shamela bron (via `shamela`) | Verificatie‑logica (hardening) |
|---|---|---|
| `format_specific_metadata.shamela_book_id` | bookId input / master.books[].id citeturn1search1 | Altijd opslaan; vormt join‑key voor rechecks. |
| `title_arabic` | master.books[].name en/of book metadata citeturn1search1 | Normaliseer hamza/ya/ta marbuta; meet edit distance; grote drift → `METADATA_INCONSISTENCY`. fileciteturn7file0L1-L1 |
| `author.name_arabic` | master.authors (join via book.authorId/author) citeturn1search1 | Als Shamela author ≠ LLM author maar titel matcht sterk: treat als disambiguation case → human gate. |
| `page_count` | `getBook()` geeft pages[] en page count citeturn1search1 | Cross-check tegen jouw extract; mismatch → `PAGE_COUNT_MISMATCH`. fileciteturn7file0L1-L1 |
| `structural_format`/`is_multi_layer` | titles[] (TOC), footnote splits via content utils citeturn1search1 | Detecteer “body vs footer” consistentie; als structure ontbreekt → `FORMAT_STRUCTURE_MISSING`. fileciteturn7file0L1-L1 |
| `format_specific_metadata.shamela_category` | master.categories citeturn1search1 | Gebruik categorie als genre prior; conflict → `needs_review_fields += ['genre']`. fileciteturn7file0L1-L1 |

Belangrijk: `shamela` vereist API‑config (API key, endpoints) en kan master/book DB downloaden als `.db/.sqlite` of JSON. citeturn1search0turn1search1 Dat maakt het geschikt voor jouw “freeze” mental model: je kunt de master versie + boekversie pinnen en later deterministic replays draaien.

## Evaluatiemethodologie voor HUNT mode: wat je kunt lenen uit OpenITI, KITAB, entity["organization","HathiTrust","digital library consortium"] en entity["organization","Europeana","eu cultural heritage platform"]

Je vraag is expliciet “methodologie op schaal”—dus minder “een paar handmatige spotchecks”, meer: sampling‑design, metrics, error taxonomies, en een proces dat je periodiek kunt herhalen.

### OpenITI/KITAB: combinatie van handgemaakte metadata + issue-driven correcties + periodieke reruns

OpenITI structureert data als corpora met CTS‑achtige URIs en YAML metadata per author/book/version. citeturn0search0 KITAB benadrukt dat corpus metadata “only be produced by hand” en dat high-quality metadata tijd kost, maar essentieel is; ze publiceren metadata bij releases en bieden ook een “latest metadata” export. citeturn4search3  
Voor jouw HUNT‑modus vertaalt dit naar een sterk patroon:

- **Stabiele releases + “latest” stream**: jouw factory kan (a) immutable frozen artifacts schrijven, (b) daarnaast een “rolling registry” onderhouden, maar altijd met provenance + version tags. Je contracts hebben al `frozen_hash`, `frozen_file_hashes`, `intake_timestamp` en metadata history hooks. fileciteturn7file0L1-L1  
- **Issue‑driven correcties**: OpenITI gebruikt expliciet issues om metadata/textproblemen te tracken; dat is een schaalbaar human feedback mechanisme. citeturn0search0  

### KITAB passim: gold truth annotatie + parameter review als evaluatie‑motor

KITAB beschrijft passim’s werking en hun eigen evaluatieproces: het is foutgevoelig bij “meaningless alignments” of gemiste reuse als parameters slecht staan; daarom werken ze met reviewed parameters en produceren evaluatie‑datasets. citeturn4search0turn4search5  
Ze hebben bovendien expliciet een “Text reuse detection evaluation” project waarin ground truth reuse geannoteerd wordt om passim te evalueren en te verbeteren. citeturn4search1  

Adaptatie voor jouw HUNT‑mode (concreet):  
- Definieer per verificatiedimensie (author, genre, madhhab, structure, decontextualisatie) een **error typology** + severity (je hebt al `ErrorCode`/`ErrorSeverity`). fileciteturn7file0L1-L1  
- Maak een gestratificeerde sample (per genre, per source_format, per trust tier) en bouw **gold labels** (niet op LLM).  
- Rerun periodiek en vergelijk drift: dit is exact het passim patroon (“we run passim at least twice every year … data … checked thoroughly to guard against errors”). citeturn4search0  

### HathiTrust/HTRC: omgaan met OCR heterogeniteit zonder perfecte quality score

HathiTrust documenteert dat OCR automatisch is, foutgevoelig, en dat misidentificatie van script/taal tot “gibberish” kan leiden; non‑Latin scripts zoals Arabisch hebben vaker hoge error rates. citeturn5search0  
HTRC benadrukt dat OCR quality varieert, dat er geen “right way” is om de best representative volume te selecteren zonder te kijken, en dat ze geen quality score aanbieden; men gebruikt proxies zoals recency of digitization. citeturn5search1  
HTRC’s Extracted Features dataset (v2.5) is een voorbeeld van “freshly processed” text+metadata op zeer grote schaal, met een vaste JSON‑LD schema‑laag en expliciete citeerpraktijk (“accessed on”). citeturn5search2  

Adaptatie voor HUNT‑mode:  
- Gebruik “proxy metrics” (bv. empty ratio, encoding suspect, page_count mismatch) als *automatische filters*; je error codes dekken dit soort signals al (`HIGH_EMPTY_RATIO`, `ENCODING_SUSPECT`, `OCR_LOW_QUALITY`). fileciteturn7file0L1-L1  
- Combineer proxies met kleine, maar goed ontworpen human audits (zoals KITAB’s ground truth). citeturn4search1  

### Europeana: tiered metadata quality als model voor jouw verificatie‑scorecards

Europeana werkt met een Data Quality Committee en een Publishing Framework met metadata quality tiers en “quality pillars” (o.a. taal, enabling elements, contextual classes). citeturn0search2turn0search48turn0search4  
Dit is direct herbruikbaar voor jouw metadata‑verificatie op schaal: je kunt je output classificeren in tiers (bv. Tier A: only extracted; Tier B: extracted + 1 independent corroboration; Tier C: majority agreement + provenance high), analoog aan Europeana’s principe “the more you give, the more you get”. citeturn0search48  

## Test- en QA tooling die specifiek helpt bij NLP/extractie-output verificatie

Je vroeg expliciet: “beyond Hypothesis en Mutmut”—dus tools die *output verification* structureren en regressies detecteren.

### Behavioral tests voor NLP/LLM‑gedrag (niet alleen accuracy)

**CheckList (methodologie + tool)**  
CheckList introduceert een task‑agnostic aanpak voor behavioral testing van NLP‑modellen: capability matrix + test types, plus tooling om veel test cases te genereren en failure patterns te vinden. citeturn6search2turn6search0  
Voor jouw factory is dit direct bruikbaar voor “decontextualisatie‑tests” en “school-of-thought framing”: je maakt templated inputs waar je verwacht dat (a) citatie niet gefabriceerd wordt, (b) tegenargument context meegeleverd wordt, (c) madhhab onzekerheid correct getoond wordt.

**TextAttack (adversarial + augmentation)**  
TextAttack biedt een framework voor adversarial attacks en data augmentation in NLP. citeturn6search15turn6search14  
Dat is bruikbaar om je extractors te stress‑testen met: spellingvarianten, hamza/ya variaties, ligaturen, en boundary perturbations (bv. footnote markers die verschuiven).

### Gestandaardiseerde evaluatie-metrics tooling

**Hugging Face Evaluate**  
De Evaluate library geeft consistente toegang tot metrics/measurements en ondersteunt reproducible evaluatie. entity["organization","Hugging Face","ml platform"] citeturn6search5  
Voor structured extraction kun je eigen metrics toevoegen (bv. “field‑level agreement rate”, “schema‑valid pass rate”, “majority‑vote corroboration rate”).

**spaCy scorer/benchmark accuracy**  
spaCy heeft een `Scorer` voor evaluation en CLI‑benchmarking om accuracy te meten op getrainde pipelines. citeturn6search17turn6search18  
Zelfs als je spaCy niet als core Arabic NLP gebruikt, is de evaluatie‑architectuur (gold vs predicted, token alignment, reporting) herbruikbaar als patroon.

### Data‑contract & regressie verificatie voor JSON/registries

**JSON Schema (Draft 2020‑12) + Python `jsonschema`**  
JSON Schema 2020‑12 is een moderne spec voor schema‑validatie. citeturn7search0 De `jsonschema` Python library ondersteunt draft 2020‑12 en kan iteratief alle validation errors rapporteren en aangeven welke properties faalden. citeturn7search3  
Voor jouw registry writes (scholars/works/sources) is dit complementair aan Pydantic: JSON Schema kan dienen als “external validator” in CI zodat contract drift vroeg detecteerbaar is.

**Pandera (DataFrame schemas)**  
Pandera laat je DataFrameSchema’s definiëren met type‑ en constraint checks en strictness. citeturn7search1  
Voor HUNT‑mode audits (bv. “alle sources met `needs_review_fields`”, “alle scholars met death_date drift”) kun je exports als tabellen valideren: “kolommen bestaan, ranges kloppen, uniqueness constraints”.

**Great Expectations (schema + integrity suites)**  
Great Expectations is expliciet gebouwd voor data quality suites: schema‑validatie over tijd en integrity checks (ook cross‑table). citeturn7search7turn7search10  
Dit sluit direct aan op jouw pipeline‑idee van “invariants” en “human gate triggers”: je kunt expectations mappen op je invariants (bv. “author_canonical_id moet bestaan in scholars registry”, “trust_score in [0,1]”, “genre ∈ enum”).

## Domeinbenchmarks die je evaluatiestack voor “Islamic knowledge” kunnen versterken

Je noemde “IslamicMMLU (March 2026)”. Ik heb geen citable public bron gevonden die precies die naam gebruikt. Wat ik wél met harde bronnen zie, zijn drie benchmarks/datasets die je dezelfde rol kunnen laten spelen (Islamic knowledge evaluation / culture‑aligned QA):

- **ArabicMMLU (MBZUAI)**: 40 taken, 14,575 multiple‑choice vragen in MSA, met o.a. een “Islamic Studies” config. citeturn9search3turn9search4  
- **ILMAAM (Arabic Culturally Aligned MMLU)**: een culture‑aligned variant met toegevoegde topics zoals Islamic Religion/Islamic History en annotaties voor o.a. religious sensitivity en social norms. citeturn10search0  
- **Dialectal-Arabic-MMLU**: MMLU‑Redux uitgebreid naar meerdere Arabische dialecten; relevant als je excerpting/metadata over verschillende Arabische registervarianten wil stress‑testen. citeturn9search0  

Daarnaast bestaat er een recente survey‑dataset (“Advances in AI Systems on Islamic Knowledge Capabilities: A Critical Survey”) die expliciet trends noemt zoals retrieval‑grounded pipelines, verification/deferral mechanisms en school‑of‑thought‑sensitive framing; bruikbaar als literatuurindex om meer bronnen/benchmarks te vinden. citeturn10search1  

## Samenvattend: de meest “high-leverage” toevoegingen aan jouw huidige stack

Als je je hardening inspanningen wil concentreren op bronnen die direct op je bestaande schema/QA‑mechanismen klikken, dan zijn dit de sterkste aanvullingen bovenop wat je al noemde:

1. **OpenITI YAML authority** als primaire “scholars.json seed” met death dates + teacher/student edges. citeturn0search0  
2. **Wikidata SPARQL** als tweede onafhankelijke graph‑laag voor madhhab (P9929) en genealogie (P1066/P802), exact passend bij je cross-validation stubs. citeturn2search7turn2search8turn2search0  
3. **Shamela v4 via `shamela` npm** niet alleen voor book metadata, maar ook als onverwachte rijal‑bron (18,989 narrator biographies export). citeturn1search1  
4. **KITAB passim + methodologie** als externe “structure evidence” layer voor matn/sharh en context‑verankering, met een bewezen evaluatiepatroon (ground truth annotatie + reruns). citeturn4search0turn4search1  
5. **OpenITI mARkdown parser/TEI converter tooling** als onafhankelijke structure parser baseline. citeturn4search6turn4search12  
6. **Europeana + HathiTrust QA patterns**: tiered metadata quality + omgaan met OCR heterogeniteit via proxies + audits, wat je direct kunt mappen op je trust tiers en error codes. citeturn0search48turn5search0turn5search1  
7. **CheckList + Great Expectations/Pandera/jsonschema** als test‑stack die specifiek output verification en regressie‑detectie in pipelines operationaliseert. citeturn6search2turn7search7turn7search1turn7search3  

Deze set geeft je precies wat je vroeg: **onafhankelijke verificatiekanalen** voor author attribution, genre, madhhab, matn/sharh structuur en (indirect) decontextualisatie, plus een realistische route om `scholars.json` te vullen en om je HUNT‑modus op schaal te evalueren met herhaalbare methodologie. fileciteturn7file0L1-L1