"""LIANA cell-cell communication helpers."""

from __future__ import annotations

from pathlib import Path
from typing import (
    Dict,
    Optional,
)

import pandas as pd

from ..graph import BubbleGraph

_LR_THRESHOLD = 0.1
_MIN_INTERACTIONS = 1


def load_results(cache_dir: Path) -> Dict[str, pd.DataFrame]:
    """Load LIANA results from a directory of parquet files.

    Returns dict keyed by filename stem (e.g. timepoint name).
    """
    return {
        f.stem: pd.read_parquet(f)
        for f in sorted(cache_dir.glob("*.parquet"))
    }


def to_graph(
    df: pd.DataFrame,
    *,
    score_col: str = "rank_score",
    threshold: float = _LR_THRESHOLD,
    min_interactions: int = _MIN_INTERACTIONS,
    node_colors: Optional[Dict[str, str]] = None,
    node_radius: float = 0.46,
) -> BubbleGraph:
    """Convert LIANA results to a BubbleGraph.

    Counts significant source->target interactions as edge weights.
    """
    sig = df[df[score_col] <= threshold].copy()
    mat = sig.groupby(["source", "target"]).size().reset_index(name="n_interactions")
    mat = mat[mat["n_interactions"] >= min_interactions]

    g = BubbleGraph()
    all_nodes = set(mat["source"]) | set(mat["target"])
    for name in all_nodes:
        g.add_node(
            name, color=(node_colors or {}).get(name, "#CCCCCC"),
            radius=node_radius,
        )
    for _, row in mat.iterrows():
        g.add_edge(row["source"], row["target"], weight=float(row["n_interactions"]))
    return g


def to_graph_filtered(
    df: pd.DataFrame,
    *,
    include: Optional[str] = None,
    score_col: str = "rank_score",
    threshold: float = _LR_THRESHOLD,
    min_interactions: int = _MIN_INTERACTIONS,
    node_colors: Optional[Dict[str, str]] = None,
    node_radius: float = 0.46,
) -> BubbleGraph:
    """Convert LIANA results, keeping only rows where source or target matches *include*.

    *include* is matched with ``str.contains``.
    """
    sig = df[df[score_col] <= threshold].copy()
    if include is not None:
        sig = sig[sig["source"].str.contains(include) | sig["target"].str.contains(include)]
    mat = sig.groupby(["source", "target"]).size().reset_index(name="n_interactions")
    mat = mat[mat["n_interactions"] >= min_interactions]

    g = BubbleGraph()
    for name in set(mat["source"]) | set(mat["target"]):
        g.add_node(
            name, color=(node_colors or {}).get(name, "#CCCCCC"),
            radius=node_radius,
        )
    for _, row in mat.iterrows():
        g.add_edge(row["source"], row["target"], weight=float(row["n_interactions"]))
    return g


def merge_nodes(
    graph: BubbleGraph,
    pattern: str,
    merged_label: str,
    merged_color: str = "#911EB4",
) -> BubbleGraph:
    """Merge all nodes whose name contains *pattern* into a single node."""
    from collections import defaultdict

    agg: Dict[Tuple[str, str], float] = defaultdict(float)
    for e in graph.edges:
        src = merged_label if pattern in e.source else e.source
        tgt = merged_label if pattern in e.target else e.target
        agg[(src, tgt)] += e.weight

    g = BubbleGraph()
    merged_added = False
    for name, node in graph.nodes.items():
        if pattern in name:
            if not merged_added:
                g.add_node(
                    merged_label, color=merged_color, radius=node.radius,
                    label_position="center",
                )
                merged_added = True
        else:
            g.add_node(
                name, color=node.color, radius=node.radius,
                label=node.label, label_position=node.label_position,
            )
    for (src, tgt), w in agg.items():
        g.add_edge(src, tgt, weight=w)
    return g
