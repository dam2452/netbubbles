"""Citation network helpers - bibliographic reference graphs."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from ..graph import BubbleGraph

# ── Colour palette for paper/year groups ─────────────────────────

_YEAR_COLORS: Dict[str, str] = {}
_PALETTE = [
    "#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
    "#FF7F00", "#A65628", "#F781BF", "#999999",
]


def _year_color(year: int) -> str:
    bucket = str((year // 3) * 3)
    if bucket not in _YEAR_COLORS:
        _YEAR_COLORS[bucket] = _PALETTE[len(_YEAR_COLORS) % len(_PALETTE)]
    return _YEAR_COLORS[bucket]


# ── BibTeX parsing ───────────────────────────────────────────────

_BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{", re.IGNORECASE)
_BIB_FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^}]*)\}")


def parse_bibtex(path: str | Path) -> List[Dict[str, str]]:
    """Parse a .bib file and return a list of entry dicts.

    Each dict has at minimum ``key``, ``type`` fields and whatever
    fields were defined in the entry (``title``, ``author``, ``year``, etc.).
    """
    text = Path(path).read_text(encoding="utf-8")
    entries: List[Dict[str, str]] = []
    for m in _BIB_ENTRY_RE.finditer(text):
        entry_type = m.group(1).lower()
        start = m.end()
        depth = 1
        pos = start
        while pos < len(text) and depth > 0:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        body = text[start:pos - 1]
        fields: Dict[str, str] = {"type": entry_type}
        for fm in _BIB_FIELD_RE.finditer(body):
            fields[fm.group(1).lower()] = fm.group(2).strip()
        key_match = re.match(r"\s*([^,\s]+)\s*,", body)
        if key_match:
            fields["key"] = key_match.group(1)
        entries.append(fields)
    return entries


# ── Graph builders ───────────────────────────────────────────────

def to_graph(
    entries: List[Dict[str, str]],
    *,
    citation_map: Optional[Dict[str, List[str]]] = None,
    mode: str = "paper",
    node_radius: float = 0.46,
    color_by: str = "year",
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Convert parsed bibliography entries to a BubbleGraph.

    Parameters
    ----------
    entries:
        List of dicts as returned by :func:`parse_bibtex`.
    citation_map:
        Dict mapping entry keys to lists of keys they cite.
        If *None*, no edges are created (just nodes).
    mode:
        ``"paper"`` - one node per paper (default).
        ``"author"`` - aggregate to first-author level.
    color_by:
        ``"year"`` - colour by publication year bucket.
        ``"type"`` - colour by entry type (article, book, …).
    """
    if mode == "author":
        return _author_graph(entries, citation_map, node_radius, node_colors)

    g = BubbleGraph()
    for e in entries:
        key = e.get("key", "")
        if not key:
            continue
        label = e.get("title", key)[:40]
        if color_by == "year" and "year" in e:
            color = _year_color(int(e["year"]))
        elif color_by == "type":
            idx = hash(e.get("type", "article")) % len(_PALETTE)
            color = _PALETTE[idx]
        else:
            color = "#CCCCCC"
        color = (node_colors or {}).get(key, color)
        g.add_node(
            key, color=color, radius=node_radius, label=label,
            label_position="outer", label_fontsize=9,
        )

    if citation_map:
        for src, targets in citation_map.items():
            for tgt in targets:
                if src in g.nodes and tgt in g.nodes:
                    g.add_edge(src, tgt, weight=1.0)

    return g


def _author_graph(
    entries: List[Dict[str, str]],
    citation_map: Optional[Dict[str, List[str]]],
    node_radius: float,
    node_colors: Optional[Dict[str, str]],
) -> BubbleGraph:
    key_to_author: Dict[str, str] = {}
    for e in entries:
        key = e.get("key", "")
        author_field = e.get("author", "")
        first = author_field.split(" and ")[0].split(",")[0].strip() if author_field else key
        key_to_author[key] = first

    g = BubbleGraph()
    author_set = set(key_to_author.values())
    for a in sorted(author_set):
        color = (node_colors or {}).get(a, "#CCCCCC")
        g.add_node(a, color=color, radius=node_radius)

    if citation_map:
        agg: Dict[Tuple[str, str], float] = defaultdict(float)
        for src, targets in citation_map.items():
            for tgt in targets:
                a_src = key_to_author.get(src)
                a_tgt = key_to_author.get(tgt)
                if a_src and a_tgt and a_src != a_tgt:
                    agg[(a_src, a_tgt)] += 1.0
        for (s, t), w in agg.items():
            g.add_edge(s, t, weight=w)

    return g
