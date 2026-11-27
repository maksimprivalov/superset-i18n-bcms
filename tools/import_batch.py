#!/usr/bin/env python3
"""Write translations from a JSON batch back into a catalog.

Input JSON (the output of export_batch.py with translations filled in, or a
minimal file of the same shape):
  {"version": "6.1.0", "lang": "sr_Latn", "reviewed": false,
   "entries": [{"msgid": "...", "msgid_plural": null, "msgstr": "...",
                "note": "optional reason, kept as a comment"},
               {"msgid": "...", "msgid_plural": "...", "msgstr": ["form0", "form1", "form2"]}]}

Imported entries are marked fuzzy with the translator comment
"Machine-translated (Claude), needs native review", unless the batch sets
"reviewed": true (only the maintainer does that). Each entry is checked with
the structural checks first; failing entries are not written. Entries that are
already translated and not fuzzy are skipped unless --overwrite.

For sr_Latn the Cyrillic sr catalog is regenerated afterwards.

Usage: python tools/import_batch.py build/batch.json [--overwrite]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import dump, load, structural_problems  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MT_COMMENT = "Machine-translated (Claude), needs native review"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("batch", type=Path)
    ap.add_argument("--overwrite", action="store_true", help="also replace reviewed (non-fuzzy) translations")
    ap.add_argument("--no-sr", action="store_true", help="do not regenerate sr after importing sr_Latn")
    args = ap.parse_args()

    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    version, lang, reviewed = batch["version"], batch["lang"], bool(batch.get("reviewed", False))
    po = ROOT / "versions" / version / "superset" / "translations" / lang / "LC_MESSAGES" / "messages.po"
    catalog = load(po, locale=lang)
    index = {(m.id if isinstance(m.id, str) else m.id[0]): m for m in catalog if m.id}

    imported = skipped = failed = 0
    for entry in batch["entries"]:
        key = entry["msgid"]
        value = entry.get("msgstr")
        if value in (None, "", []):
            continue
        msg = index.get(key)
        if msg is None:
            print(f"  ! not in catalog: {key[:70]!r}")
            failed += 1
            continue
        is_plural = isinstance(msg.id, (tuple, list))
        if is_plural != isinstance(value, list) or (is_plural and entry.get("msgid_plural") not in (None, msg.id[1])):
            print(f"  ! singular/plural mismatch: {key[:70]!r}")
            failed += 1
            continue
        current = list(msg.string) if is_plural else [msg.string]
        if all(current) and not msg.fuzzy and not args.overwrite:
            skipped += 1
            continue
        old_string = msg.string
        msg.string = tuple(value) if is_plural else value
        problems = structural_problems(msg, catalog.num_plurals)
        if is_plural and len(value) != catalog.num_plurals:
            problems.append(f"expected {catalog.num_plurals} plural forms, got {len(value)}")
        if problems:
            msg.string = old_string
            print(f"  ! rejected {key[:70]!r}: {'; '.join(problems)}")
            failed += 1
            continue
        comments = [] if reviewed else [MT_COMMENT]
        if entry.get("note"):
            comments.append(entry["note"])
        msg.user_comments = comments
        if reviewed:
            msg.flags.discard("fuzzy")
        else:
            msg.flags.add("fuzzy")
        imported += 1

    dump(catalog, po)
    print(f"{po.relative_to(ROOT).as_posix()}: imported {imported}, skipped {skipped} (already reviewed), "
          f"rejected {failed}")
    if lang == "sr_Latn" and not args.no_sr:
        import transliterate_sr
        transliterate_sr.main_regenerate()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
