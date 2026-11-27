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
4. Run the checks (`tools/check.py`, to be added) before opening a pull request.

## Review workflow

- Machine-drafted entries are marked `#, fuzzy` and carry the comment
  `Machine-translated (Claude), needs native review`.
- A native speaker reviews an entry, corrects it if needed, and removes both the
  `fuzzy` flag and the comment.
- Only the maintainer marks entries as reviewed.

## Commits

Conventional Commits in English, one logical change per commit, for example
`fix(hr): use "nadzorna ploča" consistently`.
