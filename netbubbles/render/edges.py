"""Edge drawing orchestration."""

from __future__ import annotations

import math
from typing import (
    Dict,
    Set,
    Tuple,
)

import matplotlib.pyplot as plt
import numpy as np

from ..graph import (
    BubbleGraph,
    Edge,
)
from ..style import Style
from .arrows import (
    draw_arrow,
    draw_self_loop,
)
from .geometry import (
    compute_bow_signs,
    compute_spread_angles,
    inward_angle,
)
from .nodes import node_border_half_data


def _bg_radius(
    style: Style,
    pos: Dict[str, Tuple[float, float]],
) -> float:
    if style.background_circles:
        return max(abs(cy) + r for _, cy, r, _ in style.background_circles)
    if pos:
        return max(np.sqrt(x ** 2 + y ** 2) for x, y in pos.values()) * 0.95
    return math.inf


def _edge_style_params(
    edge: Edge, frac: float, style: Style,
) -> Tuple[str, float, float]:
    return (
        edge.color or style.edge_color(frac),
        edge.linewidth or style.edge_linewidth(frac),
        edge.alpha or style.edge_alpha(frac),
    )


def draw_edges(
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
    constrain_angles: bool,
) -> None:
    edges = graph.edges
    if not edges:
        return

    sorted_edges = sorted(edges, key=lambda e: e.weight, reverse=True)
    top = sorted_edges[:style.max_edges]
    if not top:
        return

    border_half = node_border_half_data(ax, style)
    weights = [e.weight for e in top]
    max_w, min_w = max(weights), min(weights)

    regular = [e for e in top if not e.is_self_loop]
    edge_keys = {(e.source, e.target) for e in regular}
    bidirectional = {k for k in edge_keys if (k[1], k[0]) in edge_keys}
    start_ang, end_ang = compute_spread_angles(regular, pos, constrain_angles, style.arrow_spread_rad, style.arrow_arc_limit_rad)
    bow_signs = compute_bow_signs(regular, pos)
    bg_r = _bg_radius(style, pos)

    for edge in top:
        if edge.source not in pos or edge.target not in pos:
            continue
        _draw_single_edge(ax, edge, graph, pos, style, border_half, bg_r,
                          min_w, max_w, start_ang, end_ang, bow_signs, bidirectional)


def _draw_single_edge(  # pylint: disable=too-many-arguments
    ax: plt.Axes,
    edge: Edge,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
    border_half: float,
    bg_r: float,
    min_w: float, max_w: float,
    start_ang: Dict[Tuple[str, str], float],
    end_ang: Dict[Tuple[str, str], float],
    bow_signs: Dict[Tuple[str, str], float],
    bidirectional: Set[Tuple[str, str]],
) -> None:
    frac = (edge.weight - min_w) / (max_w - min_w + 1e-9)
    color, lw, alpha = _edge_style_params(edge, frac, style)
    r_src = graph.nodes[edge.source].radius + (border_half if style.arrow_tail_hugs_border else 0.0)
    r_tgt = graph.nodes[edge.target].radius + border_half

    if edge.is_self_loop:
        draw_self_loop(ax, pos[edge.source], r_src, color, lw, alpha, style)
    else:
        key = (edge.source, edge.target)
        _draw_directed_edge(ax, edge, pos, style, r_src, r_tgt, bg_r,
                            color, lw, alpha, start_ang, end_ang, bow_signs,
                            key in bidirectional)


def _draw_directed_edge(  # pylint: disable=too-many-arguments
    ax: plt.Axes,
    edge: Edge,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
    r_src: float, r_tgt: float, bg_r: float,
    color: str, lw: float, alpha: float,
    start_ang: Dict[Tuple[str, str], float],
    end_ang: Dict[Tuple[str, str], float],
    bow_signs: Dict[Tuple[str, str], float],
    is_bidirectional: bool,
) -> None:
    key = (edge.source, edge.target)
    sa = start_ang.get(key, inward_angle(pos[edge.source]))
    ea = end_ang.get(key, inward_angle(pos[edge.target]))
    bow = bow_signs.get(key, 1.0)
    draw_arrow(
        ax, pos[edge.source], pos[edge.target],
        r_src, r_tgt, sa, ea, bow, bg_r, color, lw, alpha, style, is_bidirectional,
    )
