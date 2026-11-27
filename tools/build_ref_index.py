#!/usr/bin/env python3
"""Build a msgid -> source references index for a Superset version.

Superset's messages.pot is extracted with --no-location, so catalogs carry no
`#:` references. This runs the same extraction as upstream babel_update.sh
(same babel.cfg and keywords) on a local checkout of that version, keeps the
locations, and writes them to build/refs-<version>.json (gitignored). The
catalogs and the template are not touched.

Usage:
  python tools/build_ref_index.py --source .upstream --version 6.1.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KEYWORDS = ["-k", "_", "-k", "__", "-k", "t", "-k", "tn:1,2", "-k", "tct"]  # as in babel_update.sh


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, type=Path, help="checkout of apache/superset at that version")
    ap.add_argument("--version", required=True)
    args = ap.parse_args()

    out = ROOT / "build" / f"refs-{args.version}.json"
    with tempfile.TemporaryDirectory() as tmp:
        pot = Path(tmp) / "refs.pot"
        cmd = [sys.executable, "-m", "babel.messages.frontend", "extract", "-F",
               "superset/translations/babel.cfg", "-o", str(pot), *KEYWORDS, "--sort-output", "."]
        subprocess.run(cmd, cwd=args.source, check=True, stdout=subprocess.DEVNULL)
        refs: dict[str, list[str]] = defaultdict(list)
        for msg in load(pot):
            if msg.id:
                key = msg.id if isinstance(msg.id, str) else msg.id[0]
                refs[key].extend(sorted({path.replace("\\", "/") for path, _line in msg.locations}))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(refs, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")

    template = load(args.source / "superset" / "translations" / "messages.pot")
    ids = [m.id if isinstance(m.id, str) else m.id[0] for m in template if m.id]
    covered = sum(1 for i in ids if refs.get(i))
    print(f"wrote {out.relative_to(ROOT).as_posix()}: {len(refs)} msgids; "
          f"{covered}/{len(ids)} template msgids have references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
