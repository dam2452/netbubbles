"""Edge drawing orchestration."""

from __future__ import annotations

import math
from typing import (
    Dict,
    Optional,
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
    _bezier_ctrl,
    draw_arrow,
    draw_self_loop,
)
from .geometry import (
    compute_bow_signs,
    compute_spread_angles,
    inward_angle,
    is_dense_layout,
)
from .nodes import node_border_half_data


def _resolve_high_density(
    style: Style,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
) -> bool:
    val = style.high_density
    if isinstance(val, bool):
        return val
    normalized = str(val).strip().lower()
    if normalized in ("on", "true", "yes", "1"):
        return True
    if normalized in ("off", "false", "no", "0"):
        return False
    radii = {name: node.radius for name, node in graph.nodes.items()}
    return is_dense_layout(pos, radii)


def _bezier_point(
    start: Tuple[float, float],
    ctrl: Tuple[float, float],
    end: Tuple[float, float],
    t: float,
) -> Tuple[float, float]:
    mt = 1.0 - t
    return (mt * mt * start[0] + 2 * mt * t * ctrl[0] + t * t * end[0],
            mt * mt * start[1] + 2 * mt * t * ctrl[1] + t * t * end[1])


def _adjust_ctrl_avoidance(
    ctrl: Tuple[float, float],
    start: Tuple[float, float],
    end: Tuple[float, float],
    src_name: str,
    tgt_name: str,
    graph: "BubbleGraph",
    pos: Dict[str, Tuple[float, float]],
    margin: float = 0.08,
    iterations: int = 4,
) -> Tuple[float, float]:
    cx, cy = ctrl
    sample_ts = [0.2, 0.4, 0.5, 0.6, 0.8]
    for _ in range(iterations):
        push_x, push_y = 0.0, 0.0
        for t in sample_ts:
            bx, by = _bezier_point(start, (cx, cy), end, t)
            for name, node_pos in pos.items():
                if name in (src_name, tgt_name):
                    continue
                nx, ny = node_pos
                r = graph.nodes[name].radius + margin
                dx, dy = bx - nx, by - ny
                dist = np.sqrt(dx * dx + dy * dy) + 1e-9
                if dist < r:
                    strength = (r - dist) / r
                    push_x += dx / dist * strength
                    push_y += dy / dist * strength
        if abs(push_x) < 1e-6 and abs(push_y) < 1e-6:
            break
        cx += push_x * 0.5
        cy += push_y * 0.5
    return (cx, cy)


def _adjust_ctrls_for_overlap(
    ctrl_overrides: Dict[Tuple[str, str], Tuple[float, float]],
    edge_endpoints: Dict[Tuple[str, str], Tuple[Tuple[float, float], Tuple[float, float]]],
    bg_radius: float,
    overlap_threshold: float = 0.18,
    bow_step: float = 0.07,
    iterations: int = 8,
) -> Dict[Tuple[str, str], Tuple[float, float]]:
    keys = list(ctrl_overrides.keys())
    sample_ts = [0.25, 0.5, 0.75]
    result = dict(ctrl_overrides)

    for _ in range(iterations):
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                ka, kb = keys[i], keys[j]
                start_a, end_a = edge_endpoints[ka]
                start_b, end_b = edge_endpoints[kb]
                ctrl_a, ctrl_b = result[ka], result[kb]
                hits = sum(
                    1 for t in sample_ts
                    if np.sqrt(
                        (_bezier_point(start_a, ctrl_a, end_a, t)[0] - _bezier_point(start_b, ctrl_b, end_b, t)[0]) ** 2 +
                        (_bezier_point(start_a, ctrl_a, end_a, t)[1] - _bezier_point(start_b, ctrl_b, end_b, t)[1]) ** 2
                    ) < overlap_threshold
                )
                if hits == 0:
                    continue
                cx, cy = result[kb]
                start_p, end_p = edge_endpoints[kb]
                mx = (start_p[0] + end_p[0]) / 2.0
                my = (start_p[1] + end_p[1]) / 2.0
                bx, by = cx - mx, cy - my
                bd = np.sqrt(bx ** 2 + by ** 2) + 1e-9
                step = bow_step * hits
                nx, ny = cx + bx / bd * step, cy + by / bd * step
                nd = np.sqrt(nx ** 2 + ny ** 2) + 1e-9
                if nd > bg_radius:
                    nx, ny = nx * bg_radius / nd, ny * bg_radius / nd
                result[kb] = (nx, ny)

    return result


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
    dense = _resolve_high_density(style, graph, pos)

    edge_keys = {(e.source, e.target) for e in regular}
    bidirectional = {k for k in edge_keys if (k[1], k[0]) in edge_keys} if dense else set()
    start_ang, end_ang = compute_spread_angles(
        regular, pos, constrain_angles,
        style.arrow_spread_rad, style.arrow_arc_limit_rad, dense,
    )
    bow_signs = compute_bow_signs(regular, pos, dense)
    bg_r = _bg_radius(style, pos)

    ctrl_overrides: Dict[Tuple[str, str], Tuple[float, float]] = {}
    if dense:
        edge_endpoints: Dict[Tuple[str, str], Tuple[Tuple[float, float], Tuple[float, float]]] = {}
        for edge in regular:
            if edge.source not in pos or edge.target not in pos:
                continue
            key = (edge.source, edge.target)
            r_src = graph.nodes[edge.source].radius + (border_half if style.arrow_tail_hugs_border else 0.0)
            r_tgt = graph.nodes[edge.target].radius + border_half
            sa = start_ang.get(key, inward_angle(pos[edge.source]))
            ea = end_ang.get(key, inward_angle(pos[edge.target]))
            bow = bow_signs.get(key, 1.0)
            p1, p2 = pos[edge.source], pos[edge.target]
            start_pt = (p1[0] + r_src * np.cos(sa), p1[1] + r_src * np.sin(sa))
            end_pt = (p2[0] + r_tgt * np.cos(ea), p2[1] + r_tgt * np.sin(ea))
            ctrl = _bezier_ctrl(start_pt, end_pt, p1, p2, bow, style.curve_strength, bg_r, True, key in bidirectional)
            ctrl = _adjust_ctrl_avoidance(ctrl, start_pt, end_pt, edge.source, edge.target, graph, pos)
            ctrl_overrides[key] = ctrl
            edge_endpoints[key] = (start_pt, end_pt)
        ctrl_overrides = _adjust_ctrls_for_overlap(ctrl_overrides, edge_endpoints, bg_r)

    for edge in reversed(top):
        if edge.source not in pos or edge.target not in pos:
            continue
        _draw_single_edge(ax, edge, graph, pos, style, border_half, bg_r,
                          min_w, max_w, start_ang, end_ang, bow_signs, dense,
                          bidirectional, ctrl_overrides)


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
    dense: bool,
    bidirectional: Set[Tuple[str, str]],
    ctrl_overrides: Dict[Tuple[str, str], Tuple[float, float]],
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
                            dense, key in bidirectional, ctrl_overrides.get(key))


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
    dense: bool,
    is_bidirectional: bool,
    ctrl_override: Optional[Tuple[float, float]],
) -> None:
    key = (edge.source, edge.target)
    sa = start_ang.get(key, inward_angle(pos[edge.source]))
    ea = end_ang.get(key, inward_angle(pos[edge.target]))
    bow = bow_signs.get(key, 1.0)
    p1, p2 = pos[edge.source], pos[edge.target]
    draw_arrow(
        ax, p1, p2, r_src, r_tgt, sa, ea, bow, bg_r, color, lw, alpha, style,
        dense, is_bidirectional, ctrl_override,
    )
