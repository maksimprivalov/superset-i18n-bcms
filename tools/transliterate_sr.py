#!/usr/bin/env python3
"""Generate the Serbian Cyrillic catalog (sr) from the Latin one (sr_Latn).

sr_Latn is the source of truth; sr is never edited by hand. Only msgstr is
transliterated. msgids, flags, comments and plural layout are copied, and the
Language/Language-Team headers are set to sr.

Text that stays in Latin script:
  1. placeholders (%s, %(name)s, {name}), HTML tags and entities, URLs and
     connection strings (scheme://...), e-mail addresses, `code` spans,
     keyboard shortcuts (Ctrl + Enter, Cmd / Ctrl + C, ...);
  2. quoted or bracketed ASCII text copied verbatim from the msgid
     ('value', "value", „value“, [column]);
  3. terms listed in DO_NOT_TRANSLATE.txt (case-sensitive, whole words; a
     Serbian case ending after a hyphen is still transliterated: SQL-u -> SQL-у);
  4. dotted names and paths (deck.gl, d3.js, sqlalchemy.create_engine,
     superset.example.com, sql/protocolv1/o/12345), file extensions (.pdf),
     and escape sequences written out as text (\\n);
  5. code-like words copied from the msgid: ALL-CAPS (SQL, CSV, SELECT),
     containing a digit or underscore (OAuth2, slice_id, 1D), or camelCase
     (GeoJSON, DataFrame, ECharts). The same shapes are transliterated when
     the word is not in the msgid (ILI, sloj_anotacije are Serbian);
  6. words with letters outside the Serbian Latin alphabet (Excel, Python,
     px, µs), which cannot be transliterated anyway.
Everything else is transliterated letter by letter, with lj/nj/dž -> љ/њ/џ
(also LJ/Lj, NJ/Nj, DŽ/Dž and the single code points ǉ ǌ ǆ ...), except in a
few words where the pair is two letters (injekcija, konjunkcija, nadživeti...).

Usage:
  python tools/transliterate_sr.py            # regenerate sr for every version
  python tools/transliterate_sr.py --check    # exit 1 if any sr catalog is stale
  python tools/transliterate_sr.py --text "Primeni filtere na SQL upit"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from babel import Locale

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import _BRACE_RE, _PRINTF_RE, _TAG_RE, load, read_terms, to_bytes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DNT_FILE = ROOT / "DO_NOT_TRANSLATE.txt"

_SINGLE = dict(zip("abcčćdđefghijklmnoprsštuvzž", "абцчћдђефгхијклмнопрсштувзж"))
_SINGLE.update({k.upper(): v.upper() for k, v in list(_SINGLE.items())})
_DIGRAPHS = {
    "lj": "љ", "Lj": "Љ", "LJ": "Љ", "nj": "њ", "Nj": "Њ", "NJ": "Њ", "dž": "џ", "Dž": "Џ", "DŽ": "Џ",
    "ǉ": "љ", "ǈ": "Љ", "Ǉ": "Љ", "ǌ": "њ", "ǋ": "Њ", "Ǌ": "Њ", "ǆ": "џ", "ǅ": "Џ", "Ǆ": "Џ",
}
_DIGRAPH_RE = re.compile("|".join(sorted(map(re.escape, _DIGRAPHS), key=len, reverse=True)))
# Word stems in which "nj"/"dž" are two letters, not one; offset = split position.
_SPLIT_STEMS = {"injek": 2, "konjunk": 3, "konjug": 3, "vanjez": 3, "nadživ": 3, "podžan": 3}
_ZWJ = "‍"

# Serbian Latin letters, plus accented vowels used for disambiguation (kôd).
_SERBIAN_LATIN = set("abcčćdđefghijklmnoprsštuvzž" "àáâèéêìíîòóôùúûȁȅȉȍȕ")
_KEYS = r"(?:Ctrl|ctrl|Cmd|cmd|Shift|shift|Alt|alt|Option|Meta|Esc|Enter|Return|Tab|Del|Backspace|Space)"
_EXACT_RES = [
    re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.S),           # Jinja: {{ metric }}
    _PRINTF_RE,
    _BRACE_RE,
    _TAG_RE,
    re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);"),
    re.compile(r"\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s\"'<>„“”»]*[^\s\"'<>„“”».,;:!?)]"),
    re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b"),
    re.compile(r"`[^`\n]*`"),
    re.compile(rf"\b{_KEYS}\b(?:\s*[+/]\s*(?:{_KEYS}\b|[A-Za-z0-9]\b))*"),
    re.compile(r"\\[ntr0]"),                                        # \n written as text
    re.compile(r"(?<![\w.])[A-Za-z0-9][\w\-]*(?:\.[A-Za-z_][\w\-]*)+"),  # deck.gl, a.b.c, host.com
    re.compile(r"(?<!\S)(?=[\w./\-]*\d)[\w.\-]+(?:/[\w.\-]+){2,}"),  # paths: 2+ slashes and a digit
    re.compile(r"\b[A-Za-z_]\w*=[A-Za-z0-9_\-]+"),                  # key=value: freq=W-MON
    re.compile(r"\b[A-Za-z_]\w*\(\)"),                              # function calls: float()
    re.compile(r"(?<=[^\s.])\.[A-Za-z][A-Za-z0-9]{1,4}\b"),         # file extensions: x.pdf
]
_QUOTED_RE = re.compile(r"'([^'\n]+)'|\"([^\"\n]+)\"|„([^“”\n]+)[“”]|“([^”\n]+)”|\[([^\]\n]+)\]")
_WORD_RE = re.compile(r"\w+")
_LETTER = r"A-Za-z0-9_ČĆĐŠŽčćđšž"
_DIGRAPH_CAPS = {"LJ", "NJ", "DŽ"}


def _dnt_regex(terms: list[str]) -> re.Pattern | None:
    if not terms:
        return None
    alts = "|".join(re.escape(t) for t in sorted(set(terms), key=len, reverse=True))
    return re.compile(rf"(?<![{_LETTER}])(?:{alts})(?![{_LETTER}])")


def _code_like(word: str) -> bool:
    if "_" in word or any(c.isdigit() for c in word):
        return True
    if len(word) >= 2 and re.fullmatch(r"[A-Z]+", word):
        return True
    if re.search(r"[a-z][A-Z]", word):
        return True
    m = re.search(r"([A-Z]{2})[a-z]", word)
    return bool(m and m.group(1) not in _DIGRAPH_CAPS)


def _keep_word(word: str, msgid_words: set[str]) -> bool:
    letters = [c for c in word if c.isalpha()]
    if not letters:
        return False
    if any(c.lower() not in _SERBIAN_LATIN for c in letters):
        return True
    return _code_like(word) and word in msgid_words


def _translit_plain(text: str) -> str:
    for stem, offset in _SPLIT_STEMS.items():
        text = re.sub(re.escape(stem), lambda m: m.group()[:offset] + _ZWJ + m.group()[offset:], text, flags=re.I)
    text = _DIGRAPH_RE.sub(lambda m: _DIGRAPHS[m.group()], text)
    return "".join(_SINGLE.get(c, c) for c in text).replace(_ZWJ, "")


def latin_to_cyrillic(text: str, msgid: str = "", dnt: re.Pattern | None = None) -> str:
    protected = [False] * len(text)

    def protect(start: int, end: int) -> None:
        for i in range(start, end):
            protected[i] = True

    for rx in _EXACT_RES:
        for m in rx.finditer(text):
            protect(*m.span())
    for m in _QUOTED_RE.finditer(text):
        group = next(g for g in range(1, 6) if m.group(g) is not None)
        inner = m.group(group)
        if re.fullmatch(r"[\x20-\x7e]+", inner) and inner in msgid:
            protect(*m.span(group))
    if dnt:
        for m in dnt.finditer(text):
            protect(*m.span())
    # Word rules see only the unprotected text, so "%(min)spx" yields the word "px".
    masked = "".join("\0" if p else c for c, p in zip(text, protected))
    msgid_words = set(_WORD_RE.findall(msgid))
    for m in _WORD_RE.finditer(masked):
        if _keep_word(m.group(), msgid_words):
            protect(*m.span())

    out, i = [], 0
    while i < len(text):
        j = i
        while j < len(text) and protected[j] == protected[i]:
            j += 1
        chunk = text[i:j]
        out.append(chunk if protected[i] else _translit_plain(chunk))
        i = j
    return "".join(out)


def transliterate_catalog(src: Path, dnt: re.Pattern | None) -> bytes:
    catalog = load(src, locale="sr_Latn")
    catalog.locale = Locale.parse("sr")
    catalog.language_team = "sr <LL@li.org>"
    catalog.header_comment = catalog.header_comment.replace(
        "Serbian (Latin) translations", "Serbian translations")
    for msg in catalog:
        if not msg.id:
            continue
        msgid = " ".join(msg.id) if isinstance(msg.id, (tuple, list)) else msg.id
        if isinstance(msg.string, (tuple, list)):
            msg.string = tuple(latin_to_cyrillic(s, msgid, dnt) for s in msg.string)
        else:
            msg.string = latin_to_cyrillic(msg.string, msgid, dnt)
    return to_bytes(catalog)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if a generated sr catalog is out of date")
    ap.add_argument("--text", help="transliterate one string and print it")
    ap.add_argument("--msgid", default="", help="source text for --text (enables rule 2)")
    args = ap.parse_args()
    dnt = _dnt_regex(read_terms(DNT_FILE))

    if args.text is not None:
        print(latin_to_cyrillic(args.text, args.msgid, dnt))
        return 0

    stale = 0
    for src in sorted(ROOT.glob("versions/*/superset/translations/sr_Latn/LC_MESSAGES/messages.po")):
        dst = src.parent.parent.parent / "sr" / "LC_MESSAGES" / "messages.po"
        data = transliterate_catalog(src, dnt)
        rel = dst.relative_to(ROOT).as_posix()
        if args.check:
            if not dst.exists() or dst.read_bytes() != data:
                print(f"stale: {rel} (run tools/transliterate_sr.py)", file=sys.stderr)
                stale += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print(f"wrote {rel}")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
