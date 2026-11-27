# superset-i18n-bcms

Unofficial Serbian, Croatian and Bosnian UI translations for
[Apache Superset](https://github.com/apache/superset).

> **Status: in progress.** Serbian catalogs for 6.1.0 exist, but nothing has
> been released yet and nothing in this repository is ready to install.

## What this is

Drop-in `.po` catalogs, laid out exactly like upstream
`superset/translations/<lang>/LC_MESSAGES/`, so they can be installed into a
Superset image and later submitted upstream unchanged.

| Language              | Locale code     | Script   | Variant    | Notes |
|-----------------------|-----------------|----------|------------|-------|
| Serbian (Latin)       | `sr_Latn`       | Latin    | ekavian    | Source catalog for Serbian; same code as upstream |
| Serbian (Cyrillic)    | `sr`            | Cyrillic | ekavian    | Generated from `sr_Latn`, never edited by hand |
| Croatian              | `hr`            | Latin    | ijekavian  | |
| Bosnian               | `bs`            | Latin    | ijekavian  | |
| Montenegrin           | deferred        | Latin    | ijekavian  | `cnr` does not work with Babel (it maps to `sr_Latn_ME`) |

## Supported Superset versions

| Superset | Catalog path                                  |
|----------|-----------------------------------------------|
| 6.1.0    | `versions/6.1.0/superset/translations/<lang>/` |

## Install

_To be written._ CI will build `.mo` and `messages.json` files and attach them to
GitHub Releases; `docker/` will contain an example derived image.

## Review status

See [REVIEW_STATUS.md](REVIEW_STATUS.md). Machine-drafted strings are marked
`#, fuzzy` until a native speaker reviews them. Superset serves fuzzy strings,
so drafts are visible in the UI.

## Known limitations

- **Embedded dashboards stay in English on Superset 6.1.0**, whatever locale is
  set ([apache/superset#42433](https://github.com/apache/superset/issues/42433)).
  The fix ([apache/superset#42438](https://github.com/apache/superset/pull/42438),
  merged to `master` on 2026-08-29) is not in 6.1.0. It is included in the
  7.0.0 release candidates.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). This project is
not affiliated with or endorsed by the Apache Software Foundation.

---

## Srpski (ukratko)

Nezvanični prevodi korisničkog interfejsa Apache Superseta na srpski (latinica i
ćirilica), hrvatski i bosanski. Projekat je u pripremi i još nema prevoda
spremnih za instalaciju. Mašinski prevedeni nizovi su označeni kao `fuzzy` dok ih
ne pregleda izvorni govornik. Ugrađene (embedded) kontrolne table u verziji
6.1.0 ostaju na engleskom (apache/superset#42433).
