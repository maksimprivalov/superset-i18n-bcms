# Glossary

> **DRAFT, not approved.** Proposed in Phase 0 (2026-11-27). Nothing will be
> translated against it until the maintainer approves it. "Native check" marks
> entries where a native speaker should decide.

Approved UI terminology for all target languages. `tools/check.py` warns when a
translation uses a term that conflicts with this table.

- **sr_Latn**: Serbian, Latin script, ekavian.
- **sr**: Serbian, Cyrillic. Generated from `sr_Latn` by deterministic
  transliteration, never edited by hand.
- **hr**: Croatian, ijekavian, with Croatian vocabulary (stupac, tablica, spremi,
  postavke, izvješće, tjedan).
- **bs**: Bosnian, ijekavian, with Bosnian vocabulary (kolona, tabela, sačuvaj,
  izvještaj, sedmica).
- Buttons use the imperative (Primeni / Primijeni). Labels and titles use a noun
  or nominal phrase. In UI text, capitalise only the first word.
- "= upstream" means the `sr_Latn` term matches apache/superset `master`'s
  reviewed Serbian catalog. "DEVIATES" means this draft proposes a different term.
- Product names, SQL keywords and technical tokens (Superset, SQL Lab, ECharts,
  deck.gl, Jinja, CSV, JSON, SUM, COUNT, GROUP BY…) stay in English. See
  [DO_NOT_TRANSLATE.txt](DO_NOT_TRANSLATE.txt).

## Core objects

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Dashboard | kontrolna tabla | контролна табла | nadzorna ploča | kontrolna ploča | sr = upstream (159×; 7× "kontrolni panel" upstream → normalize). bs: native check (alt. "nadzorna ploča"). |
| Chart | grafikon | графикон | grafikon | grafikon |  |
| Dataset | skup podataka | скуп података | skup podataka | skup podataka | pl. skupovi podataka. = upstream. |
| Virtual dataset | virtuelni skup podataka | виртуелни скуп података | virtualni skup podataka | virtuelni skup podataka | hr: virtualni. |
| Physical dataset | fizički skup podataka | физички скуп података | fizički skup podataka | fizički skup podataka |  |
| Metric | metrika | метрика | metrika | metrika | = upstream. |
| Dimension | dimenzija | димензија | dimenzija | dimenzija |  |
| Column | kolona | колона | stupac | kolona | hr: stupac, never "kolona". |
| Calculated column | izračunata kolona | израчуната колона | izračunati stupac | izračunata kolona |  |
| Row | red | ред | redak | red | hr: redak (gen. retka). |
| Row limit | ograničenje redova | ограничење редова | ograničenje redaka | ograničenje redova | = upstream. |
| Table | tabela | табела | tablica | tabela |  |
| Database | baza podataka | база података | baza podataka | baza podataka |  |
| Schema | šema | шема | shema | šema |  |
| Catalog | katalog | каталог | katalog | katalog |  |
| Data source / Datasource | izvor podataka | извор података | izvor podataka | izvor podataka |  |
| Query | upit | упит | upit | upit |  |
| Saved query | sačuvani upit | сачувани упит | spremljeni upit | sačuvani upit |  |
| SQL Lab | SQL Lab | SQL Lab | SQL Lab | SQL Lab | Product feature name → DO_NOT_TRANSLATE. |
| Explore (chart editor) | istraži | истражи | istraži | istraži | = upstream. |
| Visualization type | tip vizualizacije | тип визуализације | vrsta vizualizacije | tip vizualizacije |  |
| Template | šablon | шаблон | predložak | šablon | CSS template → CSS šablon / CSS predložak. |
| Theme | tema | тема | tema | tema |  |
| Tag | oznaka | ознака | oznaka | oznaka |  |

## Filters and time

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Filter | filter | филтер | filtar | filter | hr: filtar, pl. filtri, gen. pl. filtara. |
| Native filter (dashboard filter) | filter kontrolne table | филтер контролне табле | filtar nadzorne ploče | filter kontrolne ploče | Superset's dashboard-level filters. Avoid literal "izvorni/nativni filter". |
| Filter bar | traka filtera | трака филтера | traka filtara | traka filtera |  |
| Cross-filter | ukršteni filter | укрштени филтер | unakrsni filtar | unakrsni filter | sr = upstream majority (14× ukršteni, 3× unakrsni) → normalize. |
| Cross-filtering | ukršteno filtriranje | укрштено филтрирање | unakrsno filtriranje | unakrsno filtriranje |  |
| Scope (filter scope) | opseg | опсег | opseg | opseg | = upstream. |
| Default value | podrazumevana vrednost | подразумевана вредност | zadana vrijednost | zadana vrijednost |  |
| Value | vrednost | вредност | vrijednost | vrijednost |  |
| Time range | vremenski opseg | временски опсег | vremenski raspon | vremenski raspon | sr: upstream uses "opseg" 24×, "raspon" 1× → normalize to "opseg". |
| Time grain | vremenska granularnost | временска грануларност | vremenska granularnost | vremenska granularnost | Bucket size (day, week…). = upstream. |
| Time column | vremenska kolona | временска колона | vremenski stupac | vremenska kolona |  |
| Time comparison | vremensko poređenje | временско поређење | vremenska usporedba | vremensko poređenje |  |
| Rolling window | klizni prozor | клизни прозор | klizni prozor | klizni prozor |  |
| Relative / Specific (date) | relativno / određeno | релативно / одређено | relativno / određeno | relativno / određeno | Time range picker modes. |
| Now | sada | сада | sada | sada |  |
| Start / End | početak / kraj | почетак / крај | početak / kraj | početak / kraj |  |
| Day / Week / Month | dan / nedelja / mesec | дан / недеља / месец | dan / tjedan / mjesec | dan / sedmica / mjesec | Key lexical split between the four. |
| Quarter / Year | kvartal / godina | квартал / година | tromjesečje / godina | kvartal / godina | hr alt. "kvartal": native check. |
| Last week (rolling) | poslednja nedelja | последња недеља | posljednji tjedan | posljednja sedmica | Means "last 7 days", not the previous calendar week. |
| Previous calendar week | prethodna kalendarska nedelja | претходна календарска недеља | prethodni kalendarski tjedan | prethodna kalendarska sedmica |  |

## Analysis

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Aggregate | agregat / agregiraj | агрегат / агрегирај | agregat / agregiraj | agregat / agregiraj | SQL functions (SUM, COUNT…) → DO_NOT_TRANSLATE. |
| Group by | grupiši po | групиши по | grupiraj po | grupiši po | hr: -irati, sr/bs: -isati. |
| Sort by | sortiraj po | сортирај по | sortiraj po | sortiraj po | hr alt. "poredaj po": native check. |
| Ascending / Descending | rastuće / opadajuće | растуће / опадајуће | uzlazno / silazno | rastuće / opadajuće |  |
| Sum / Average / Count (labels) | zbir / prosek / broj | збир / просек / број | zbroj / prosjek / broj | zbir / prosjek / broj | UI labels only. |
| Percentage | procenat | проценат | postotak | procenat |  |
| Series | serija | серија | niz | serija | hr: native check ("niz podataka" in spreadsheets). |
| Legend | legenda | легенда | legenda | legenda |  |
| Tooltip (chart hover) | oblačić | облачић | oblačić | oblačić | sr = upstream (19×; 9× "opis"). hr/bs: native check. |
| X-axis / Y-axis | X osa / Y osa | X оса / Y оса | os X / os Y | X osa / Y osa | hr: os (f.). |
| Pivot table | pivot tabela | пивот табела | zaokretna tablica | pivot tabela |  |
| Heatmap | toplotna mapa | топлотна мапа | toplinska karta | toplotna mapa |  |
| Map | mapa | мапа | karta | mapa |  |
| Number format | format broja | формат броја | format broja | format broja |  |
| Currency | valuta | валута | valuta | valuta |  |
| Color scheme | šema boja | шема боја | shema boja | šema boja |  |
| Annotation | anotacija | анотација | anotacija | anotacija | hr alt. "bilješka": native check. |
| Annotation layer | sloj anotacija | слој анотација | sloj anotacija | sloj anotacija | = upstream. |
| Drill to detail | prikaz detalja | приказ детаља | prikaz detalja | prikaz detalja | = upstream. |
| Drill by | detaljno po | детаљно по | detaljno po | detaljno po | = upstream. |
| Samples | uzorci | узорци | uzorci | uzorci |  |
| Results | rezultati | резултати | rezultati | rezultati |  |

## Dashboard UI

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Tab (dashboard tab) | kartica | картица | kartica | kartica |  |
| Header | zaglavlje | заглавље | zaglavlje | zaglavlje |  |
| Certified | sertifikovano | сертификовано | certificirano | certificirano |  |
| Published / Draft | objavljeno / nacrt | објављено / нацрт | objavljeno / skica | objavljeno / nacrt |  |
| Favorite | omiljeno | омиљено | omiljeno | omiljeno |  |
| Full screen | ceo ekran | цео екран | cijeli zaslon | cijeli ekran | hr: zaslon (screen), never "ekran". |
| Screenshot | snimak ekrana | снимак екрана | snimka zaslona | snimak ekrana |  |
| Thumbnail | sličica | сличица | sličica | sličica |  |
| Cache | keš | кеш | predmemorija | keš |  |
| Permalink | trajna veza | трајна веза | trajna poveznica | trajna veza | sr = upstream. |
| Link | veza | веза | poveznica | veza |  |
| Clipboard | privremena memorija | привремена меморија | međuspremnik | međuspremnik | DEVIATES from upstream sr "klipbord" (8×; 3× "memorija"). Your call. |
| Embed / Embedded dashboard | ugradi / ugrađena kontrolna tabla | угради / уграђена контролна табла | ugradi / ugrađena nadzorna ploča | ugradi / ugrađena kontrolna ploča |  |

## Alerts, access, admin

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Alert | upozorenje | упозорење | upozorenje | upozorenje | = upstream. |
| Report | izveštaj | извештај | izvješće | izvještaj | ekavian / hr lexical / ijekavian. |
| Alerts & reports | upozorenja i izveštaji | упозорења и извештаји | upozorenja i izvješća | upozorenja i izvještaji |  |
| Schedule | raspored | распоред | raspored | raspored |  |
| Owner | vlasnik | власник | vlasnik | vlasnik |  |
| Role | uloga | улога | uloga | uloga |  |
| Permission | dozvola | дозвола | dopuštenje | dozvola | sr = upstream (27×). |
| User / Group | korisnik / grupa | корисник / група | korisnik / grupa | korisnik / grupa |  |
| Row level security | bezbednost na nivou reda | безбедност на нивоу реда | sigurnost na razini retka | sigurnost na nivou reda |  |
| Settings | podešavanja | подешавања | postavke | postavke |  |
| Language | jezik | језик | jezik | jezik |  |
| Email | e-pošta | е-пошта | e-pošta | e-pošta |  |
| File | datoteka | датотека | datoteka | datoteka |  |

## Actions (buttons: imperative)

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Apply | primeni | примени | primijeni | primijeni |  |
| Save | sačuvaj | сачувај | spremi | sačuvaj |  |
| Cancel | otkaži | откажи | odustani | otkaži |  |
| Delete | obriši | обриши | izbriši | izbriši | bs: native check (alt. "obriši"). |
| Clear / Clear all | očisti / očisti sve | очисти / очисти све | očisti / očisti sve | očisti / očisti sve | DEVIATES from upstream sr "Obriši sve" (12×), to keep it distinct from Delete. Your call. |
| Edit | uredi | уреди | uredi | uredi |  |
| Close | zatvori | затвори | zatvori | zatvori |  |
| Share | podeli | подели | podijeli | podijeli |  |
| Copy | kopiraj | копирај | kopiraj | kopiraj |  |
| Download | preuzmi | преузми | preuzmi | preuzmi |  |
| Upload | otpremi | отпреми | prenesi | otpremi | hr/bs: native check. |
| Export | izvezi (izvoz) | извези (извоз) | izvezi (izvoz) | izvezi (izvoz) |  |
| Import | uvezi (uvoz) | увези (увоз) | uvezi (uvoz) | uvezi (uvoz) |  |
| Refresh | osveži | освежи | osvježi | osvježi |  |
| Force refresh | prinudno osveži | принудно освежи | prisilno osvježi | prinudno osvježi | DEVIATES from upstream sr "Forsiraj osvežavanje". |
| Run (query) | izvrši | изврши | pokreni | pokreni | sr = upstream "Izvrši". |
| Stop | zaustavi | заустави | zaustavi | zaustavi |  |
| Undo / Redo | opozovi / ponovi | опозови / понови | poništi / ponovi | poništi / ponovi | Upstream sr "Poništi" is fuzzy (and Latin in the Cyrillic catalog). |
| Search | pretraži (pretraga) | претражи (претрага) | pretraži (pretraživanje) | pretraži (pretraga) |  |
| Select all | izaberi sve | изабери све | odaberi sve | odaberi sve |  |
| View as table | prikaži kao tabelu | прикажи као табелу | prikaži kao tablicu | prikaži kao tabelu | = upstream. |
| Retry | pokušaj ponovo | покушај поново | pokušaj ponovno | pokušaj ponovo |  |
| Sign in / Log out | prijavi se / odjavi se | пријави се / одјави се | prijavi se / odjavi se | prijavi se / odjavi se |  |

## States

| en | sr_Latn | sr | hr | bs | Notes |
|---|---|---|---|---|---|
| Loading... | Učitavanje... | Учитавање... | Učitavanje... | Učitavanje... |  |
| No data | nema podataka | нема података | nema podataka | nema podataka |  |
| Error | greška | грешка | pogreška | greška |  |
| Custom / Advanced | prilagođeno / napredno | прилагођено / напредно | prilagođeno / napredno | prilagođeno / napredno |  |
