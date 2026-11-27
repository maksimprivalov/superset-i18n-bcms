#!/usr/bin/env python3
"""Build release artifacts: .mo and messages.json next to each .po, in the
exact layout Superset expects, plus an optional zip.

  dist/<version>/superset/translations/<lang>/LC_MESSAGES/messages.{po,mo,json}

- .mo: compiled with fuzzy entries included, i.e. what
  `pybabel compile --use-fuzzy` writes (babel.messages.mofile.write_mo).
  Babel's compile checks run first. The only errors allowed are on
  literal-percent labels ("% of total"), which Babel 2.17 always reads as
  python-format (see common.is_literal_percent). Any other error fails the build.
- messages.json: produced by upstream's po2json (--po2json PATH), using the
  command from superset-frontend/scripts/po2json.sh at 6.1.0:
  `po2json --domain superset --format jed1.x --fuzzy <po> <json>`.

Usage:
  python tools/build.py --version 6.1.0 [--lang sr_Latn ...] [--po2json PATH]
  python tools/build.py --tag 6.1.0-sr_Latn.1 --po2json PATH --zip
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from babel.messages.mofile import write_mo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import is_literal_percent, load, msgids  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TAG_RE = re.compile(r"^(?P<version>\d+\.\d+\.\d+)-(?P<lang>[A-Za-z_]+)\.(?P<build>\d+)$")


def compile_mo(po: Path, mo: Path, lang: str) -> list[str]:
    catalog = load(po, locale=lang)
    errors = []
    for msg, errs in catalog.check():
        if errs and not is_literal_percent(*msgids(msg)):
            errors += [f"{po}: {msgids(msg)[0][:60]!r}: {e}" for e in errs]
    if not errors:
        mo.parent.mkdir(parents=True, exist_ok=True)
        with open(mo, "wb") as fh:
            write_mo(fh, catalog, use_fuzzy=True)
    return errors


def build_json(po2json: str, po: Path, out: Path) -> list[str]:
    exe = str(Path(po2json).resolve()) if Path(po2json).exists() else po2json
    cmd = [exe, "--domain", "superset", "--format", "jed1.x", "--fuzzy", str(po), str(out)]
    # npm installs a .cmd shim on Windows, which needs the shell.
    res = subprocess.run(cmd, capture_output=True, text=True, shell=sys.platform == "win32")
    if res.returncode != 0 or not out.exists():
        return [f"{po}: po2json failed: {(res.stderr or res.stdout).strip()[:300]}"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", help="Superset version under versions/")
    ap.add_argument("--lang", action="append", help="only these languages (default: all)")
    ap.add_argument("--tag", help="release tag <version>-<lang|all>.<n>, e.g. 6.1.0-sr_Latn.1")
    ap.add_argument("--po2json", help="path to upstream po2json (npm po2json@0.4.5); skip JSON if omitted")
    ap.add_argument("--out", type=Path, default=ROOT / "dist")
    ap.add_argument("--zip", action="store_true", help="also write dist/superset-translations-<tag|version>.zip")
    args = ap.parse_args()

    version, langs, label = args.version, args.lang, args.version
    if args.tag:
        m = TAG_RE.match(args.tag)
        if not m:
            print(f"bad tag {args.tag!r}; expected e.g. 6.1.0-sr_Latn.1 or 6.1.0-all.2", file=sys.stderr)
            return 2
        version, label = m["version"], args.tag
        langs = None if m["lang"] == "all" else [m["lang"]]
    if not version:
        ap.error("--version or --tag is required")

    src_root = ROOT / "versions" / version / "superset" / "translations"
    available = sorted(p.parent.parent.name for p in src_root.glob("*/LC_MESSAGES/messages.po"))
    if langs:
        missing = sorted(set(langs) - set(available))
        if missing:
            print(f"no catalog for {missing} in {src_root}", file=sys.stderr)
            return 2
    selected = langs or available

    out_root = args.out / version / "superset" / "translations"
    errors: list[str] = []
    for lang in selected:
        po = src_root / lang / "LC_MESSAGES" / "messages.po"
        dst = out_root / lang / "LC_MESSAGES"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(po, dst / "messages.po")
        errs = compile_mo(po, dst / "messages.mo", lang)
        if args.po2json and not errs:
            errs += build_json(args.po2json, dst / "messages.po", dst / "messages.json")
        errors += errs
        built = sorted(p.name for p in dst.iterdir())
        print(f"{lang}: {'FAILED' if errs else 'built ' + ', '.join(built)}")

    for e in errors:
        print(f"  ERROR {e}", file=sys.stderr)
    if errors:
        return 1

    if args.zip:
        zpath = args.out / f"superset-translations-{label}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for lang in selected:
                for f in sorted((out_root / lang / "LC_MESSAGES").iterdir()):
                    zf.write(f, f"superset/translations/{lang}/LC_MESSAGES/{f.name}")
        print(f"wrote {zpath.relative_to(ROOT).as_posix() if zpath.is_relative_to(ROOT) else zpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
