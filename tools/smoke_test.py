#!/usr/bin/env python3
"""Smoke-test built artifacts in dist/ against their source catalogs.

Backend (.mo): loads each catalog with babel.support.Translations, the loader
Flask-Babel uses, and checks that every translated entry (fuzzy included)
comes back unchanged, and that plural entries pick the right form for
n = 1, 2, 5, 11, 21, 22, 25, 101 under the catalog's Plural-Forms rule.

Frontend (messages.json, if present): checks the Jed 1.x layout that
superset-core's Translator reads (domain "superset", locale_data.superset[""]
with lang and plural_forms), and that every translated entry has the msgstr.
Loading through the real Jed library is done by tools/smoke_jed.cjs.

Usage: python tools/smoke_test.py --version 6.1.0 [--dist dist] [--require-json]
"""

from __future__ import annotations

import argparse
import gettext
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NS = (1, 2, 5, 11, 21, 22, 25, 101)


def strings(msg) -> list[str]:
    return list(msg.string) if isinstance(msg.string, (tuple, list)) else [msg.string]


def check_lang(version: str, lang: str, dist: Path, require_json: bool) -> list[str]:
    errors: list[str] = []
    src = ROOT / "versions" / version / "superset" / "translations" / lang / "LC_MESSAGES" / "messages.po"
    built = dist / version / "superset" / "translations" / lang / "LC_MESSAGES"
    catalog = load(src, locale=lang)
    plural = gettext.c2py(catalog.plural_expr)

    mo = built / "messages.mo"
    if not mo.exists():
        return [f"{lang}: {mo} missing"]
    with open(mo, "rb") as fh:
        t = gettext.GNUTranslations(fh)
    if t.info().get("language") != lang:
        errors.append(f"{lang}: .mo Language header is {t.info().get('language')!r}")
    checked = 0
    for msg in catalog:
        if not msg.id or not all(strings(msg)):
            continue
        checked += 1
        if isinstance(msg.id, (tuple, list)):
            for n in NS:
                want = msg.string[plural(n)]
                got = t.ngettext(msg.id[0], msg.id[1], n)
                if got != want:
                    errors.append(f"{lang}: .mo ngettext({msg.id[0][:40]!r}, n={n}) = {got[:40]!r}, want {want[:40]!r}")
                    break
        elif t.gettext(msg.id) != msg.string:
            errors.append(f"{lang}: .mo gettext({msg.id[:50]!r}) differs")

    js = built / "messages.json"
    if js.exists():
        pack = json.loads(js.read_text(encoding="utf-8"))
        data = pack.get("locale_data", {}).get("superset", {})
        head = data.get("", {})
        if pack.get("domain") != "superset" or head.get("domain") != "superset":
            errors.append(f"{lang}: messages.json domain is not 'superset'")
        if head.get("lang") != lang:
            errors.append(f"{lang}: messages.json lang is {head.get('lang')!r}")
        want_pf = catalog.mime_headers and dict(catalog.mime_headers).get("Plural-Forms", "")
        if head.get("plural_forms", "").rstrip(";") != want_pf.rstrip(";"):
            errors.append(f"{lang}: messages.json plural_forms {head.get('plural_forms')!r} != {want_pf!r}")
        for msg in catalog:
            if not msg.id or not all(strings(msg)):
                continue
            key = msg.id if isinstance(msg.id, str) else msg.id[0]
            if data.get(key) != strings(msg):
                errors.append(f"{lang}: messages.json[{key[:50]!r}] = {str(data.get(key))[:60]}, want {strings(msg)!r:.60}")
                break
    elif require_json:
        errors.append(f"{lang}: {js} missing")

    print(f"{lang}: {checked} entries checked in .mo"
          + (", messages.json layout and entries checked" if js.exists() else ", no messages.json")
          + (f" -> {len(errors)} problems" if errors else " -> OK"))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True)
    ap.add_argument("--lang", action="append")
    ap.add_argument("--dist", type=Path, default=ROOT / "dist")
    ap.add_argument("--require-json", action="store_true")
    args = ap.parse_args()
    root = args.dist / args.version / "superset" / "translations"
    langs = args.lang or sorted(p.parent.parent.name for p in root.glob("*/LC_MESSAGES/messages.mo"))
    if not langs:
        print(f"nothing built under {root}", file=sys.stderr)
        return 1
    errors = [e for lang in langs for e in check_lang(args.version, lang, args.dist, args.require_json)]
    for e in errors[:50]:
        print(f"  ERROR {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
