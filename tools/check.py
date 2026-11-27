#!/usr/bin/env python3
"""Validate the translation catalogs under versions/.

Errors (exit 1):
  - structural: placeholders (%(name)s, %s, %d, {}, {0}, {name}, %%), HTML tags,
    Markdown link targets / ** markers, leading/trailing
    whitespace, newline count, missing plural forms (tools/common.py);
  - a DO_NOT_TRANSLATE.txt term present in the msgid but missing from the
    translation;
  - msgids differ from the version's template (with --template);
  - msgfmt --check-format failures (when msgfmt is on PATH; --require-msgfmt
    makes a missing msgfmt an error).
Warnings (exit 0): a different number of `code` spans, and glossary
deviations, i.e. a GLOSSARY.md source term in the
msgid whose approved translation (matched by stem, so inflected forms count)
does not appear in the translation. Printed for fuzzy (draft) entries; only
counted for reviewed ones unless --all-warnings.

Usage:
  python tools/check.py [--template 6.1.0=.upstream/superset/translations/messages.pot]
                        [--lang sr_Latn] [--require-msgfmt] [--all-warnings]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import code_spans, load, read_terms, structural_problems  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GLOSSARY = ROOT / "GLOSSARY.md"
DNT_FILE = ROOT / "DO_NOT_TRANSLATE.txt"
GLOSSARY_LANG_COLUMNS = {"sr_Latn": 1, "sr": 2, "hr": 3, "bs": 4}
_WORD = r"A-Za-z0-9_ČĆĐŠŽčćđšžА-Яа-яЂЈЉЊЋЏђјљњћџ"


# ---------------------------------------------------------------- glossary
def _alternatives(cell: str) -> list[str]:
    """'izvezi (izvoz)' -> ['izvezi', 'izvoz']; 'X osa / Y osa' stays split by caller."""
    cell = cell.strip()
    inner = re.findall(r"\(([^)]*)\)", cell)
    base = re.sub(r"\s*\([^)]*\)", "", cell).strip()
    return [t for t in [base, *inner] if t]


def _stem_regex(term: str) -> re.Pattern:
    """Each word of the term must start a word of the translation. Endings are
    dropped so inflections match: two letters of words longer than 5
    (kontrolna tabla -> kontrolnu tablu, kontrolnih tabli), one letter of
    shorter words (osa -> ose)."""
    parts = []
    for w in term.lower().split():
        if len(w) > 5:
            stem = w[: max(4, len(w) - 2)]
        elif len(w) > 3 or (len(w) == 3 and w[-1] in "aeiou"):
            stem = w[:-1]  # osa -> os (ose, osi), uredi -> ured
        else:
            stem = w
        parts.append(rf"(?<![{_WORD}]){re.escape(stem)}")
    return re.compile(".*".join(parts), re.S)


def load_glossary(lang: str) -> list[tuple[str, re.Pattern, list[re.Pattern], str]]:
    """[(english term, source regex, [accepted target regexes], display)]"""
    col = GLOSSARY_LANG_COLUMNS.get(lang)
    if col is None or not GLOSSARY.exists():
        return []
    rules = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| en |"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        en_cell = re.sub(r"\s*\([^)]*\)", "", cells[0]).strip()
        en_parts = [p.strip() for p in en_cell.split(" / ")]
        tgt_parts = [p.strip() for p in cells[col].split(" / ")]
        pairs = zip(en_parts, tgt_parts) if len(en_parts) == len(tgt_parts) else [(p, cells[col]) for p in en_parts]
        for en, tgt in pairs:
            if not en or en.endswith("..."):
                continue
            src = re.compile(rf"(?<![A-Za-z]){re.escape(en)}(?:s|es)?(?![A-Za-z])", re.I)
            alts = [a for t in tgt.split(" / ") for a in _alternatives(t)]
            rules.append((en, src, [_stem_regex(a) for a in alts], tgt))
    return rules


# ---------------------------------------------------------------- checks
def _strings(msg) -> list[str]:
    return list(msg.string) if isinstance(msg.string, (tuple, list)) else [msg.string]


def _msgids(msg) -> list[str]:
    return list(msg.id) if isinstance(msg.id, (tuple, list)) else [msg.id]


def check_catalog(path: Path, lang: str, dnt: list[str], template: Path | None, all_warnings: bool):
    catalog = load(path, locale=lang)
    errors: list[str] = []
    warnings: list[str] = []
    counted_warnings = 0
    # The term must appear in the source as written; the translation may change
    # its case (csv -> CSV, Null -> null) but must keep the term itself.
    dnt_res = [(t, re.compile(rf"(?<![{_WORD}]){re.escape(t)}(?![{_WORD}])"),
                re.compile(rf"(?<![{_WORD}]){re.escape(t)}(?![{_WORD}])", re.I)) for t in dnt]
    glossary = load_glossary(lang)

    if template is not None:
        tmpl = {(m.id, m.context) for m in load(template) if m.id}
        mine = {(m.id, m.context) for m in catalog if m.id}
        if tmpl != mine:
            errors.append(f"msgids differ from template {template}: "
                          f"{len(tmpl - mine)} missing, {len(mine - tmpl)} extra")

    for msg in catalog:
        if not msg.id or not any(_strings(msg)):
            continue
        label = repr(_msgids(msg)[0][:70])
        for p in structural_problems(msg, catalog.num_plurals):
            errors.append(f"{label}: {p}")
        source = " ".join(_msgids(msg))
        translation = " ".join(s for s in _strings(msg) if s)
        for term, rx, rx_any_case in dnt_res:
            if rx.search(source) and not rx_any_case.search(translation):
                errors.append(f"{label}: do-not-translate term {term!r} missing from translation")
        if code_spans(source) != code_spans(translation) and (msg.fuzzy or all_warnings):
            warnings.append(f"{label}: number of `code` spans differs")
        for en, src, targets, display in glossary:
            if src.search(source) and not any(t.search(translation.lower()) for t in targets):
                if msg.fuzzy or all_warnings:
                    warnings.append(f"{label}: glossary {en!r} -> {display!r}")
                else:
                    counted_warnings += 1
                break
    return errors, warnings, counted_warnings


def run_msgfmt(path: Path) -> list[str]:
    exe = shutil.which("msgfmt")
    if exe is None:
        return []
    res = subprocess.run([exe, "--check-format", "--use-fuzzy", "-o", "-", str(path)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode == 0:
        return []
    return [f"msgfmt: {line}" for line in res.stderr.splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template", action="append", default=[], metavar="VERSION=POT",
                    help="check msgids against this template (repeatable)")
    ap.add_argument("--lang", action="append", help="only these languages")
    ap.add_argument("--require-msgfmt", action="store_true", help="fail if msgfmt is not installed")
    ap.add_argument("--all-warnings", action="store_true", help="print glossary warnings for reviewed entries too")
    args = ap.parse_args()

    templates = dict(t.split("=", 1) for t in args.template)
    dnt = read_terms(DNT_FILE)
    have_msgfmt = shutil.which("msgfmt") is not None
    if not have_msgfmt:
        msg = "msgfmt not found: msgfmt --check-format skipped"
        if args.require_msgfmt:
            print(f"ERROR: {msg}", file=sys.stderr)
            return 1
        print(f"WARNING: {msg}")

    total_errors = 0
    for path in sorted(ROOT.glob("versions/*/superset/translations/*/LC_MESSAGES/messages.po")):
        lang = path.parent.parent.name
        version = path.parents[4].name
        if args.lang and lang not in args.lang:
            continue
        template = Path(templates[version]) if version in templates else None
        errors, warnings, counted = check_catalog(path, lang, dnt, template, args.all_warnings)
        errors += run_msgfmt(path)
        rel = path.relative_to(ROOT).as_posix()
        print(f"{rel}: {len(errors)} errors, {len(warnings) + counted} glossary warnings"
              + (f" ({counted} on reviewed entries, not listed)" if counted else ""))
        for e in errors:
            print(f"  ERROR   {e}")
        for w in warnings:
            print(f"  warning {w}")
        total_errors += len(errors)
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
