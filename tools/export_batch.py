#!/usr/bin/env python3
"""Export a batch of untranslated (or fuzzy) entries to JSON for translation.

Each entry carries what a translator needs: msgid, msgid_plural, flags,
source references (from build/refs-<version>.json, see build_ref_index.py),
comments, the current translation if any, translations of the same msgid in
other upstream languages, and the most similar reviewed strings from another
catalog of the same language (e.g. upstream master), for consistency.

Areas (CLAUDE.md priority order; an entry belongs to the first that matches):
  priority  what a dashboard viewer sees (dashboard, native filters, time range,
            chart header menus, cross-filters, drill, empty/error/loading states)
  explore   chart editing, chart plugins and controls
  sqllab    SQL Lab
  data      datasets, databases, settings, admin
  other     everything else (including entries without references)

Usage:
  python tools/export_batch.py --version 6.1.0 --lang sr_Latn --area priority \\
      --similar-git .upstream ad1abef52ee4ab6812570d2db20103ac28aae730 -o build/batch.json
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load, load_bytes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_LANGS = ["sl", "ru", "uk", "pl", "sk", "de", "fr", "es"]
AREAS = [
    ("priority", re.compile(
        r"src/dashboard/|nativeFilters|NativeFilters|FilterBar|DateFilterControl|SliceHeaderControls"
        r"|src/components/Chart|crossFilter|CrossFilter|DrillDetail|DrillBy|drillBy|drillDetail"
        r"|src/components/(EmptyState|ErrorMessage|Loading|ErrorBoundary)|src/components/TimeRange"
        r"|src/components/(Dropdown|Menu|Modal|Tooltip|Popover)")),
    ("explore", re.compile(r"src/explore/|plugins/|packages/superset-ui-chart-controls|packages/superset-ui-core"
                           r"|src/visualizations|src/components/(AlteredSliceTag|Datasource)|superset/viz\.py")),
    ("sqllab", re.compile(r"src/SqlLab/|sqllab|sql_lab")),
    ("data", re.compile(r"src/features/|src/pages/|superset/(databases|datasets|db_engine_specs|connectors"
                        r"|security|commands|views|models|daos|utils|reports|tags|themes)")),
]


def area_of(refs: list[str]) -> str:
    for name, rx in AREAS:
        if any(rx.search(r) for r in refs):
            return name
    return "other"


def strings(msg) -> list[str]:
    return list(msg.string) if isinstance(msg.string, (tuple, list)) else [msg.string]


def is_translated(msg) -> bool:
    s = strings(msg)
    return bool(s) and all(s)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True)
    ap.add_argument("--lang", required=True)
    ap.add_argument("--status", choices=["untranslated", "fuzzy", "both"], default="untranslated")
    ap.add_argument("--area", choices=[a for a, _ in AREAS] + ["other", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0, help="max entries (0 = no limit)")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--upstream", type=Path, default=ROOT / ".upstream", help="checkout with context languages")
    ap.add_argument("--similar-git", nargs=2, metavar=("REPO", "COMMIT"),
                    help="also show the closest reviewed msgids from <lang> at COMMIT in REPO")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    po = ROOT / "versions" / args.version / "superset" / "translations" / args.lang / "LC_MESSAGES" / "messages.po"
    catalog = load(po, locale=args.lang)
    refs_file = ROOT / "build" / f"refs-{args.version}.json"
    refs = json.loads(refs_file.read_text(encoding="utf-8")) if refs_file.exists() else {}
    if not refs:
        print(f"warning: {refs_file} missing; every entry falls in area 'other'", file=sys.stderr)

    context = {}
    for lang in CONTEXT_LANGS:
        p = args.upstream / "superset" / "translations" / lang / "LC_MESSAGES" / "messages.po"
        if p.exists():
            context[lang] = {m.id: m for m in load(p, locale=lang) if m.id and not m.fuzzy and is_translated(m)}

    similar_pool: dict[str, object] = {}
    if args.similar_git:
        repo, commit = args.similar_git
        data = subprocess.run(["git", "-C", repo, "show",
                               f"{commit}:superset/translations/{args.lang}/LC_MESSAGES/messages.po"],
                              capture_output=True, check=True).stdout
        similar_pool = {(m.id if isinstance(m.id, str) else m.id[0]): m
                        for m in load_bytes(data, locale=args.lang) if m.id and not m.fuzzy and is_translated(m)}
    pool_keys = list(similar_pool)

    selected = []
    for msg in catalog:
        if not msg.id:
            continue
        wanted = {"untranslated": not is_translated(msg) and not msg.fuzzy,
                  "fuzzy": msg.fuzzy,
                  "both": msg.fuzzy or not is_translated(msg)}[args.status]
        if not wanted:
            continue
        key = msg.id if isinstance(msg.id, str) else msg.id[0]
        msg_refs = refs.get(key, [])
        area = area_of(msg_refs)
        if args.area != "all" and area != args.area:
            continue
        selected.append((msg, key, msg_refs, area))

    order = {name: i for i, name in enumerate([a for a, _ in AREAS] + ["other"])}
    selected.sort(key=lambda x: order[x[3]])
    selected = selected[args.offset:]
    if args.limit:
        selected = selected[: args.limit]

    entries = []
    for msg, key, msg_refs, area in selected:
        plural = msg.id[1] if isinstance(msg.id, (tuple, list)) else None
        ctx = {}
        for lang, cat in context.items():
            other = cat.get(msg.id)
            if other is not None:
                ctx[lang] = strings(other) if plural else other.string
        similar = []
        for k in difflib.get_close_matches(key, pool_keys, n=3, cutoff=0.75):
            m = similar_pool[k]
            similar.append({"msgid": k, "msgstr": strings(m) if isinstance(m.id, (tuple, list)) else m.string})
        entries.append({
            "msgid": key,
            "msgid_plural": plural,
            "flags": sorted(msg.flags),
            "area": area,
            "references": msg_refs[:8],
            "comments": list(msg.auto_comments) + list(msg.user_comments),
            "current": strings(msg) if plural else msg.string,
            "context": ctx,
            "similar": similar,
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"version": args.version, "lang": args.lang, "nplurals": catalog.num_plurals,
                                       "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    by_area = {}
    for e in entries:
        by_area[e["area"]] = by_area.get(e["area"], 0) + 1
    print(f"wrote {len(entries)} entries to {args.output} {by_area}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
