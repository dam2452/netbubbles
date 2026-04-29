"""Data pipeline / ETL flow graph helpers."""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from ..graph import BubbleGraph

# pylint: disable=missing-param-doc



_STEP_COLORS = {
    "extract":   "#E41A1C",
    "load":      "#E41A1C",
    "transform": "#377EB8",
    "validate":  "#FF7F00",
    "filter":    "#4DAF4A",
    "aggregate": "#984EA3",
    "output":    "#4DAF4A",
    "store":     "#4DAF4A",
    "default":   "#CCCCCC",
}


def _step_color(step_type: str) -> str:
    return _STEP_COLORS.get(step_type.lower(), _STEP_COLORS["default"])


# ── Graph builder ────────────────────────────────────────────────

def to_graph(
    steps: List[Dict[str, Any]],
    *,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
    weight_key: Optional[str] = None,
) -> BubbleGraph:
    """Convert a pipeline definition to a BubbleGraph.

    Parameters
    ----------
    steps:
        List of step dicts. Each step has:
        - ``name`` (str): step name
        - ``type`` (str, optional): step type (extract, transform, etc.)
        - ``inputs`` (list[str]): names of upstream steps
        - ``outputs`` (list[str], optional): names of downstream steps
        - ``weight`` (float, optional): throughput / volume
    weight_key:
        If provided, read weight from this key in each step dict.
    """
    g = BubbleGraph()

    for step in steps:
        name = step["name"]
        stype = step.get("type", "default")
        color = (node_colors or {}).get(name, _step_color(stype))
        w = step.get(weight_key or "weight", 1.0) if weight_key else step.get("weight", 1.0)
        g.add_node(
            name, color=color, radius=node_radius, label=name,
            label_position="center",
            metadata={"type": stype, "weight": float(w) if w else 1.0},
        )

    for step in steps:
        name = step["name"]
        w = float(step.get(weight_key or "weight", 1.0) or 1.0)
        for inp in step.get("inputs", []):
            g.add_edge(inp, name, weight=w)
        for out in step.get("outputs", []):
            g.add_edge(name, out, weight=w)

    return g


def from_dag(
    edges: List[Tuple[str, str, float]],
    *,
    step_types: Optional[Dict[str, str]] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Build a pipeline graph from a simple edge list.

    Parameters
    ----------
    edges:
        List of ``(source_step, target_step, weight)`` tuples.
    step_types:
        Optional mapping of step names to types for colouring.
    """
    g = BubbleGraph()
    all_names = set()
    for src, tgt, _ in edges:
        all_names.add(src)
        all_names.add(tgt)

    for name in sorted(all_names):
        stype = (step_types or {}).get(name, "default")
        color = (node_colors or {}).get(name, _step_color(stype))
        g.add_node(
            name, color=color, radius=node_radius, label=name,
            label_position="center",
        )

    for src, tgt, w in edges:
        g.add_edge(src, tgt, weight=w)

    return g
