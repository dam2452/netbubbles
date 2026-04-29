"""Shared helpers used across preset modules."""

from __future__ import annotations

from typing import (
    Dict,
    List,
    Optional,
)

PALETTE: List[str] = [
    "#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
    "#FF7F00", "#A65628", "#F781BF", "#999999",
]


def palette_color(index: int) -> str:
    return PALETTE[index % len(PALETTE)]


def compute_depths(
    adj: Dict[str, List[str]],
    root: Optional[str],
) -> Dict[str, int]:
    """BFS depth from *root* over adjacency dict ``{node: [children]}``."""
    if root is None:
        return {}
    depths: Dict[str, int] = {root: 0}
    queue = [(root, 0)]
    visited = {root}
    while queue:
        node, d = queue.pop(0)
        for child in adj.get(node, []):
            if child not in visited:
                visited.add(child)
                depths[child] = d + 1
                queue.append((child, d + 1))
    return depths
