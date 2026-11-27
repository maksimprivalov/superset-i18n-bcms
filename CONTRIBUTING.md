# Contributing

_Stub. The full workflow will be written once the tooling in `tools/` exists._

## Reporting a bad translation

Open an issue with:

- the language (`sr_Latn`, `sr`, `hr`, `bs`) and Superset version,
- the English source text (`msgid`) and the current translation,
- where it appears in the UI (a screenshot helps),
- your suggested translation.

## Fixing a translation

1. Edit only `msgstr` in `versions/<version>/superset/translations/<lang>/LC_MESSAGES/messages.po`.
   Never edit `msgid`, references or the template.
   **Serbian:** edit `sr_Latn` only. The Cyrillic `sr` catalog is generated from it
   with `python tools/transliterate_sr.py` and must not be edited by hand
   (CI runs `tools/transliterate_sr.py --check`). To keep a word in Latin script
   in `sr`, add it to `DO_NOT_TRANSLATE.txt`.
2. Keep placeholders (`%(name)s`, `%s`, `{name}`, `%%`), markup, whitespace and `\n` exactly as in the source.
3. Follow [GLOSSARY.md](GLOSSARY.md). Do not translate anything in [DO_NOT_TRANSLATE.txt](DO_NOT_TRANSLATE.txt).
4. Run the checks before opening a pull request (CI runs the same steps, see
   `.github/workflows/validate.yml`):

   ```sh
   pip install -r tools/requirements.txt          # Python 3.11
   # template for the msgid check: a checkout of apache/superset at the version tag
   git clone --depth 1 --branch 6.1.0 --filter=blob:none --sparse https://github.com/apache/superset.git .upstream
   git -C .upstream sparse-checkout set --no-cone /superset/translations/messages.pot
   python tools/check.py --template 6.1.0=.upstream/superset/translations/messages.pot
   python tools/transliterate_sr.py --check       # after editing sr_Latn, run it without --check
   python tools/status.py --check                 # after any catalog change, run it without --check
   ```

   `tools/check.py` also runs `msgfmt --check-format` when GNU gettext is installed;
   CI requires it. To build and smoke-test the artifacts as CI does:

   ```sh
   npm install --prefix build/node-tools --ignore-scripts --no-save po2json@0.4.5 jed@1.1.1
   python tools/build.py --version 6.1.0 --po2json build/node-tools/node_modules/.bin/po2json
   python tools/smoke_test.py --version 6.1.0 --require-json
   node tools/smoke_jed.cjs build/node-tools/node_modules/jed dist/6.1.0/superset/translations/*/LC_MESSAGES/messages.json
   ```

## Review workflow

- Machine-drafted entries are marked `#, fuzzy` and carry the comment
  `Machine-translated (Claude), needs native review`.
- A native speaker reviews an entry, corrects it if needed, and removes both the
  `fuzzy` flag and the comment.
- Only the maintainer marks entries as reviewed.

## Commits

Conventional Commits in English, one logical change per commit, for example
`fix(hr): use "nadzorna ploča" consistently`.
