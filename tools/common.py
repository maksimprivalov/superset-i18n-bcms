"""Shared helpers for the catalog tools: reading/writing catalogs the way
upstream's babel_update.sh does, and per-entry structural checks.

Catalogs are written with Babel (not polib) so that wrapping and layout are
byte-identical to what upstream's ``pybabel update`` produces.
"""

from __future__ import annotations

import io
import re
from collections import Counter
from pathlib import Path

from babel.messages.catalog import PYTHON_FORMAT, Catalog, Message
from babel.messages.pofile import read_po, write_po

PO_WIDTH = 76  # pybabel default, used by upstream babel_update.sh

# Ported from apache/superset master scripts/translations/literal_percent.py
# (Apache-2.0): labels such as "% of total" or "% calculation" parse as a
# %-directive by accident ("% o", "% c"), so Babel flags them python-format and
# msgfmt then rejects any translation that does not repeat the accident. The
# 6.1.0 template still carries the flag; master swaps it for no-python-format.
_LITERAL_PERCENT = re.compile(r"(?<!%)% (?=[A-Za-z]{2})")


def is_literal_percent(*msgids: str) -> bool:
    """True if Babel sees %-directives only in literal "% word" text."""
    return any(PYTHON_FORMAT.search(m) for m in msgids) and not any(
        PYTHON_FORMAT.search(_LITERAL_PERCENT.sub(" ", m)) for m in msgids
    )


def msgids(msg: Message) -> tuple[str, ...]:
    return tuple(msg.id) if isinstance(msg.id, (tuple, list)) else (msg.id,)

# printf-style: %s, %d, %(name)s, %.2f, %%  (no space flag, so "% of" is not a placeholder)
_PRINTF_RE = re.compile(r"%%|%(?:\([^)\s]+\))?[-+0#]?\d*(?:\.\d+)?[sdifrxXeEgG]")
# str.format / JS-style: {}, {0}, {name}, {name:fmt}
_BRACE_RE = re.compile(r"\{[^{}\s]*\}")
# HTML tags: <b>, </a>, <br/>, <a href="...">  -> compared by tag name only.
# Restricted to real HTML element names: Superset also has literal labels such as
# "<new column>" or "<no type>", whose words must be translated.
_HTML_TAGS = (
    "a|abbr|b|blockquote|br|code|dd|del|div|dl|dt|em|h[1-6]|hr|i|img|ins|kbd|li|mark|ol|"
    "p|pre|q|s|small|span|strong|sub|sup|table|tbody|td|th|thead|tr|u|ul"
)
_TAG_RE = re.compile(rf"</?({_HTML_TAGS})\b[^<>]*?/?>", re.I)
_WS_EDGE_RE = re.compile(r"^(\s*).*?(\s*)$", re.S)


def placeholders(text: str) -> Counter:
    return Counter(_PRINTF_RE.findall(text)) + Counter(_BRACE_RE.findall(text))


def tags(text: str) -> Counter:
    names = Counter()
    for m in _TAG_RE.finditer(text):
        closing = m.group(0).startswith("</")
        names[("/" if closing else "") + m.group(1).lower()] += 1
    return names


def edge_whitespace(text: str) -> tuple[str, str]:
    m = _WS_EDGE_RE.match(text)
    return (m.group(1), m.group(2)) if m else ("", "")


def _pairs(msg: Message) -> list[tuple[str, str]]:
    """(source, translation) pairs to compare. Plural forms are compared with
    the plural msgid, except form 0 which is compared with the singular."""
    if isinstance(msg.id, (tuple, list)):
        singular, plural = msg.id[0], msg.id[1]
        strings = list(msg.string) if isinstance(msg.string, (tuple, list)) else [msg.string]
        return [(singular if i == 0 else plural, s) for i, s in enumerate(strings)]
    return [(msg.id, msg.string)]


def structural_problems(msg: Message, nplurals: int) -> list[str]:
    """Problems that make a translation unsafe to ship. Empty list = OK.
    Untranslated entries are not problems."""
    problems: list[str] = []
    if isinstance(msg.id, (tuple, list)):
        strings = list(msg.string) if isinstance(msg.string, (tuple, list)) else [msg.string]
        if not any(strings):
            return []
        if len(strings) != nplurals or not all(strings):
            problems.append(f"plural forms: expected {nplurals} non-empty, got {sum(1 for s in strings if s)}/{len(strings)}")
    elif not msg.string:
        return []
    is_plural = isinstance(msg.id, (tuple, list))
    # Plural forms do not map 1:1 to singular/plural: in sr/hr/bs form 0 also covers
    # 21, 31, ... so it may (and should) use the count placeholder even when the
    # English singular hardcodes "1". Allow any placeholder from either msgid.
    plural_allowed = (placeholders(msg.id[0]) | placeholders(msg.id[1])) if is_plural else Counter()
    for i, (src, dst) in enumerate(_pairs(msg)):
        if not dst:
            continue
        where = f"[{i}] " if is_plural else ""
        sp, dp = placeholders(src), placeholders(dst)
        if is_plural:
            extra = dp - plural_allowed
            if extra:
                problems.append(f"{where}unexpected placeholders {sorted(extra.elements())}")
        elif sp != dp:
            problems.append(f"{where}placeholders {sorted(sp.elements())} != {sorted(dp.elements())}")
        if tags(src) != tags(dst):
            problems.append(f"{where}markup {sorted(tags(src).elements())} != {sorted(tags(dst).elements())}")
        if edge_whitespace(src) != edge_whitespace(dst):
            problems.append(f"{where}leading/trailing whitespace differs")
        if src.count("\n") != dst.count("\n"):
            problems.append(f"{where}newline count {src.count(chr(10))} != {dst.count(chr(10))}")
    return problems


def load(path: Path | str, locale: str | None = None) -> Catalog:
    with open(path, "rb") as fh:
        return read_po(fh, locale=locale)


def load_bytes(data: bytes, locale: str | None = None) -> Catalog:
    return read_po(io.BytesIO(data), locale=locale)


def dump(catalog: Catalog, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_bytes(catalog))


def to_bytes(catalog: Catalog) -> bytes:
    """Serialize like master's babel_update.sh: pybabel layout at width 76, LF
    line endings, literal-percent entries flagged no-python-format, last
    (blank) line chopped off (python-babel/babel#799)."""
    for msg in catalog:
        if msg.id and "python-format" in msg.flags and is_literal_percent(*msgids(msg)):
            msg.flags.discard("python-format")
            msg.flags.add("no-python-format")
    buf = io.BytesIO()
    write_po(buf, catalog, width=PO_WIDTH, ignore_obsolete=True)
    data = buf.getvalue().replace(b"\r\n", b"\n")
    if data.endswith(b"\n\n"):
        data = data[:-1]
    return data


def read_terms(path: Path) -> list[str]:
    """Terms from a one-per-line list (DO_NOT_TRANSLATE.txt); '#' lines and blanks ignored."""
    if not path.exists():
        return []
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]
