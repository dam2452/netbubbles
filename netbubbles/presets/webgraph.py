"""Web link graph helpers - page-to-page hyperlink networks."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from ..graph import BubbleGraph
from ._common import (
    compute_depths,
    palette_color,
)

# pylint: disable=missing-param-doc




def _depth_color(depth: int) -> str:
    return palette_color(depth)


# ── Graph builder ────────────────────────────────────────────────

def from_links(  # pylint: disable=too-many-locals
    link_dict: Dict[str, List[str]],
    *,
    root: Optional[str] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
    label_max_length: int = 25,
) -> BubbleGraph:
    """Convert a page-link mapping to a BubbleGraph.

    Parameters
    ----------
    link_dict:
        ``{page_url: [linked_page_urls]}`` mapping.
    root:
        Root page - drawn larger. Computed automatically if *None*.
    label_max_length:
        Truncate labels longer than this.
    """
    all_pages = set(link_dict.keys())
    for targets in link_dict.values():
        all_pages.update(targets)

    if root is None:
        all_sources = set(link_dict.keys())
        root = max(all_sources, key=lambda p: len(link_dict.get(p, []))) if all_sources else None

    depths = compute_depths(link_dict, root)
    g = BubbleGraph()

    for page in sorted(all_pages):
        d = depths.get(page, 99)
        color = (node_colors or {}).get(page, _depth_color(d))
        r = node_radius * 1.3 if page == root else node_radius
        label = page if len(page) <= label_max_length else page[:label_max_length - 3] + "..."
        lp = "center" if page == root else "outer"
        g.add_node(page, color=color, radius=r, label=label, label_position=lp)

    agg: Dict[Tuple[str, str], float] = defaultdict(float)
    for src, targets in link_dict.items():
        for tgt in targets:
            agg[(src, tgt)] += 1.0

    for (src, tgt), w in agg.items():
        g.add_edge(src, tgt, weight=w)

    return g


def from_adjacency_dict(
    adj: Dict[str, Dict[str, float]],
    *,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Convert a weighted adjacency dict to a BubbleGraph.

    Parameters
    ----------
    adj:
        ``{source: {target: weight}}`` mapping.
    """
    g = BubbleGraph()
    all_pages = set(adj.keys())
    for targets in adj.values():
        all_pages.update(targets.keys())

    for page in sorted(all_pages):
        color = (node_colors or {}).get(page, "#CCCCCC")
        g.add_node(page, color=color, radius=node_radius)

    for src, targets in adj.items():
        for tgt, w in targets.items():
            g.add_edge(src, tgt, weight=w)

    return g
