#!/usr/bin/env python3
"""Create a new catalog from a Superset template (like ``pybabel init``) and
seed it with reviewed translations from an upstream catalog.

Only exact matches are copied: same msgid, same msgid_plural, same context.
Upstream entries that are fuzzy or empty are not copied, so those strings stay
untranslated here. Seeded entries keep the template's flags and get the
translator comment "Seeded from <ref> (reviewed upstream)". An entry that fails
a structural check (placeholders, markup, edge whitespace, newlines, plural
forms) is still copied, but marked fuzzy with the reason, so a person reviews it.

No network access: the source is a local file, or a commit in a local git clone.

Example:
  python tools/seed_from_upstream.py \\
      --template .upstream/superset/translations/messages.pot \\
      --source-git .upstream ad1abef52ee4ab6812570d2db20103ac28aae730 \\
      --locale sr_Latn \\
      --output versions/6.1.0/superset/translations/sr_Latn/LC_MESSAGES/messages.po
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from collections import Counter
from pathlib import Path

from babel import Locale

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import dump, load, load_bytes, structural_problems  # noqa: E402

SEED_COMMENT = "Seeded from {ref} (reviewed upstream)"


def git(repo: str, *args: str) -> bytes:
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True).stdout


def is_translated(string) -> bool:
    if isinstance(string, (tuple, list)):
        return bool(string) and all(string)
    return bool(string)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template", required=True, type=Path, help="messages.pot of the target Superset version")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--source", type=Path, help="upstream .po file to seed from")
    src.add_argument("--source-git", nargs=2, metavar=("REPO", "COMMIT"),
                     help="read superset/translations/<locale>/LC_MESSAGES/messages.po at COMMIT in local clone REPO")
    ap.add_argument("--source-locale", help="locale of the source catalog (default: --locale)")
    ap.add_argument("--source-label", help="label for the seed comment (default: apache/superset@<commit[:12]>)")
    ap.add_argument("--locale", required=True)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--revision-date", help="PO-Revision-Date, ISO 8601 (default: source commit date, or now)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing output catalog")
    args = ap.parse_args()

    if args.output.exists() and not args.force:
        print(f"refusing to overwrite {args.output} (use --force)", file=sys.stderr)
        return 2

    locale = Locale.parse(args.locale)
    source_locale = args.source_locale or args.locale
    revision = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

    if args.source_git:
        repo, commit = args.source_git
        commit = git(repo, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
        path = f"superset/translations/{source_locale}/LC_MESSAGES/messages.po"
        source = load_bytes(git(repo, "show", f"{commit}:{path}"), locale=source_locale)
        label = args.source_label or f"apache/superset@{commit[:12]}"
        revision = dt.datetime.fromisoformat(git(repo, "show", "-s", "--format=%cI", commit).decode().strip())
    else:
        source = load(args.source, locale=source_locale)
        label = args.source_label or args.source.as_posix()
    if args.revision_date:
        revision = dt.datetime.fromisoformat(args.revision_date)

    # Same steps as `pybabel init` (babel.messages.frontend.InitCatalog.run).
    catalog = load(args.template, locale=args.locale)
    catalog.locale = locale
    catalog.revision_date = revision
    catalog.fuzzy = False

    by_key = {(m.id, m.context): m for m in source if m.id}
    stats = Counter()
    flagged: list[tuple[str, list[str]]] = []
    for msg in catalog:
        if not msg.id:
            continue
        stats["template"] += 1
        up = by_key.get((msg.id, msg.context))
        if up is None:
            stats["not in upstream"] += 1
            continue
        if up.fuzzy:
            stats["upstream fuzzy (skipped)"] += 1
            continue
        if not is_translated(up.string):
            stats["upstream empty (skipped)"] += 1
            continue
        msg.string = up.string
        comment = SEED_COMMENT.format(ref=label)
        problems = structural_problems(msg, catalog.num_plurals)
        if problems:
            msg.flags.add("fuzzy")
            comment += "; failed check: " + "; ".join(problems) + "; needs review"
            stats["seeded, flagged fuzzy"] += 1
            flagged.append((msg.id if isinstance(msg.id, str) else msg.id[0], problems))
        else:
            stats["seeded"] += 1
        msg.user_comments = [comment]

    dump(catalog, args.output)

    print(f"{args.output}: locale={locale} source={label} plurals={catalog.num_plurals}")
    for key in ("template", "seeded", "seeded, flagged fuzzy", "upstream fuzzy (skipped)",
                "upstream empty (skipped)", "not in upstream"):
        print(f"  {key:26} {stats[key]:5}")
    for msgid, problems in flagged:
        print(f"  ! {msgid[:60]!r}: {'; '.join(problems)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
