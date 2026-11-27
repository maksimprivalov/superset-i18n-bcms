\# superset-i18n-bcms — unofficial Serbian / Croatian / Bosnian UI translations for Apache Superset



\## Goal

Provide ready-to-use, validated UI translations for Apache Superset, starting with \*\*Superset 6.1.0\*\*:

1\. `sr\_Latn` — Serbian, Latin script (first, primary)

2\. `sr` — Serbian, Cyrillic (generated from `sr\_Latn` by deterministic transliteration, then spot-checked)

3\. `hr` — Croatian, 4. `bs` — Bosnian (separate passes, ijekavian)

5\. Montenegrin — later, only after a decision on the locale code (Babel/CLDR support for `cnr` is uncertain)



Files must stay \*\*upstream-compatible\*\*: identical layout and format to `apache/superset`'s

`superset/translations/<lang>/LC\_MESSAGES/`, so they can later be submitted upstream unchanged.



\## Facts verified before this repo was created (re-verify, do not assume)

\- Superset 6.1.0 `messages.pot`: \~4,600 entries, \~25,600 words, 26 plural entries.

\- Upstream workflow (developer docs, "Contributing translations"): create catalogs with `pybabel init`,

&#x20; update with `scripts/translations/babel\_update.sh` (not bare `pybabel extract/update`),

&#x20; frontend JSON with `npm run build-translation` (`scripts/po2json.js`), backend `pybabel compile --use-fuzzy`.

&#x20; Upstream commits only `.po`; AI-drafted strings are marked `#, fuzzy` with an attribution comment,

&#x20; and a native reviewer removes the flag after review.

\- The official Docker image ships only `.po` files; `.mo` and frontend JSON must be built.

\- \*\*Known limitation (issue apache/superset#42433):\*\* in 6.1.0, embedded dashboards stay in English

&#x20; regardless of locale; reportedly fixed on master after 6.1.0 (PR #40729, unconfirmed). Document this

&#x20; in the README; do not promise translated embedded dashboards on 6.1.0.



\## Repository layout

```

README.md                 # English + short Serbian section: what, versions, install, review status, limitations

LICENSE                   # Apache-2.0

NOTICE                    # strings derived from Apache Superset; unofficial, not endorsed by the ASF

CONTRIBUTING.md           # how to report/fix a translation; review workflow

GLOSSARY.md               # approved terminology: en | sr\_Latn | sr | hr | bs (+ notes)

DO\_NOT\_TRANSLATE.txt      # product names, SQL keywords, technical tokens kept in English

REVIEW\_STATUS.md          # per language/version: total, reviewed, fuzzy (AI draft), untranslated

tools/                    # small Python helpers (see below); no secrets, no network calls

versions/6.1.0/superset/translations/<lang>/LC\_MESSAGES/messages.po

docker/                   # example derived image + superset\_config.py snippet

.github/workflows/        # validate on PR, build release artifacts on tag

```

Compiled `.mo` and `messages.json` are \*\*not committed\*\*; CI builds them and attaches them to GitHub Releases

(tag format: `6.1.0-sr\_Latn.1`, `6.1.0-all.2`, ...).



\## Upstream tooling

\- Clone `apache/superset` at tag `6.1.0` into `.upstream/` (gitignored, sparse checkout is fine) and use

&#x20; its `messages.pot`, `babel\_update.sh`, `po2json` script and `superset/translations/requirements.txt`.

\- Newer tooling (e.g. `scripts/translations/backfill\_po.py`, `do-not-translate.txt`) may exist only on

&#x20; `master`. If useful, read it from master, but the catalog must always match the \*\*6.1.0\*\* template.

\- Never hand-edit `msgid`, references or the template; regenerate from the template instead.



\## Helper tools to write (Python 3.11, `polib`)

\- `tools/export\_batch.py` — export N untranslated (or fuzzy) entries of a given area to JSON

&#x20; (msgid, msgid\_plural, references, comments, existing translations of the same msgid in other upstream

&#x20; languages for context).

\- `tools/import\_batch.py` — write translations back; mark imported entries `#, fuzzy` and add the comment

&#x20; `Machine-translated (Claude), needs native review` unless the batch is flagged as reviewed.

\- `tools/check.py` — fail on: placeholder mismatch (`%(name)s`, `%s`, `%d`, `{}`, `{0}`, `{name}`, `%%`),

&#x20; HTML/Markdown tag mismatch, lost leading/trailing whitespace or `\\n`, missing plural forms,

&#x20; glossary violations (warning), terms from DO\_NOT\_TRANSLATE translated (error); also runs

&#x20; `msgfmt --check-format`.

\- `tools/transliterate\_sr.py` — `sr\_Latn` → `sr` (Cyrillic): handle lj/nj/dž digraphs and their capitals;

&#x20; never touch placeholders, markup, URLs, or DO\_NOT\_TRANSLATE terms.

\- `tools/status.py` — regenerate `REVIEW\_STATUS.md`.



\## Translation rules

1\. Never change placeholders, markup, whitespace, `\\n`, or keyboard shortcuts. Never translate DO\_NOT\_TRANSLATE terms.

2\. Plural header for all target languages:

&#x20;  `Plural-Forms: nplurals=3; plural=(n%10==1 \&\& n%100!=11 ? 0 : n%10>=2 \&\& n%10<=4 \&\& (n%100<10 || n%100>=20) ? 1 : 2);`

&#x20;  Fill all three `msgstr\[n]`.

3\. Short, neutral UI language; imperative verbs on buttons (Primeni, Sačuvaj, Obriši, Otkaži);

&#x20;  consistent with GLOSSARY.md. If a string is ambiguous, read the referenced source file in `.upstream/`.

4\. `sr\_Latn` is ekavian (izveštaj, primeni); `hr` and `bs` are ijekavian (izvještaj, primijeni) and have

&#x20;  their own vocabulary — separate passes, never copy blindly.

5\. Machine drafts are always `fuzzy` until a native speaker reviews them. Only the maintainer marks

&#x20;  entries as reviewed.



\## Priority order (sr\_Latn)

1\. \*\*Priority set\*\* — what a dashboard viewer sees: native filter bar, time range picker, dashboard header

&#x20;  and menus, chart header menus (download, view as table, drill), cross-filters, empty/error/loading states.

&#x20;  Select by `#:` references (e.g. `src/dashboard/`, `nativeFilters`, `DateFilterControl`,

&#x20;  `SliceHeaderControls`, `components/Chart`, `explore/components/controls/DateFilterControl`).

2\. Explore (chart editing), 3. SQL Lab, 4. Datasets/Databases/Settings, 5. everything else.



\## Validation and release

\- CI on every PR: `tools/check.py`, `pybabel compile --use-fuzzy`, frontend JSON build with upstream po2json,

&#x20; and a smoke test that the JSON loads.

\- Release workflow on tag: build `.mo` + `messages.json` per language, attach a zip with the exact

&#x20; `superset/translations/<lang>/LC\_MESSAGES/` tree.

\- `docker/`: `FROM apache/superset:6.1.0`, copy the built files to the image's translations directory

&#x20; (verify the path inside the image), plus a `superset\_config.py` snippet with `LANGUAGES` and

&#x20; optional `BABEL\_DEFAULT\_LOCALE`. Test it if Docker is available; otherwise say clearly it is untested.



\## Working agreement

\- Work in small steps. Before each step: 3–5 sentences of what and why. After each step: a short summary

&#x20; with numbers (translated / fuzzy / reviewed / remaining) and check results.

\- \*\*Stop and ask\*\* before: choosing locale codes, approving the glossary, any release/tag, anything that

&#x20; changes the upstream-compatible layout.

\- Commits: Conventional Commits in English (e.g. `feat(sr\_Latn): priority set for dashboard viewers`),

&#x20; one logical change per commit. Never push or tag without explicit approval.

\- Do not invent Superset behaviour or config options; verify in `.upstream/` or the official docs,

&#x20; and say when something is unverified.

