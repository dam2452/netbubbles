"""Render a BubbleGraph onto matplotlib axes."""

from __future__ import annotations

from typing import (
    Dict,
    Optional,
    Tuple,
)

import matplotlib.pyplot as plt

from ..graph import BubbleGraph
from ..layout import circular as _circular_layout
from ..style import (
    Style,
    default_style,
)
from .background import (
    draw_background,
    finalize_axes,
)
from .edges import draw_edges
from .legend import add_legend
from .nodes import draw_nodes
from .title import (
    compute_content_top,
    draw_title,
)

__all__ = ["draw", "add_legend"]


def draw(
    graph: BubbleGraph,
    ax: Optional[plt.Axes] = None,
    *,
    pos: Optional[Dict[str, Tuple[float, float]]] = None,
    title: str = "",
    subtitle: str = "",
    style: Style = default_style,
    constrain_angles: bool = True,
    background: bool = True,
) -> plt.Axes:
    """Draw a BubbleGraph on *ax* (creates one if None)."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 8))
    if pos is None:
        pos = _circular_layout(graph.node_names)

    graph.positions = pos

    if style.ax_facecolor is not None:
        ax.set_facecolor(style.ax_facecolor)
    finalize_axes(ax, pos, style)
    if background:
        draw_background(ax, pos, style)
    draw_edges(ax, graph, pos, style, constrain_angles)
    draw_nodes(ax, graph, pos, style)
    content_top = compute_content_top(ax, graph, pos, style)
    draw_title(ax, title, subtitle, style, content_top)
    return ax
