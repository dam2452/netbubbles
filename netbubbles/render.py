"""Render a BubbleGraph onto matplotlib axes."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import matplotlib.patheffects as mpe
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path as MplPath
from matplotlib.transforms import ScaledTranslation

from .graph import BubbleGraph
from .style import Style, default_style


# ── Public API ───────────────────────────────────────────────────

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
        from .layout import circular
        pos = circular(graph.node_names)

    graph.positions = pos

    if style.ax_facecolor is not None:
        ax.set_facecolor(style.ax_facecolor)
    if background:
        _draw_background(ax, pos, style)
    _draw_edges(ax, graph, pos, style, constrain_angles)
    _draw_nodes(ax, graph, pos, style)
    content_top = _compute_content_top(pos, style)
    _finalize_axes(ax, pos, style)
    _draw_title(ax, title, subtitle, style, content_top)
    return ax


def add_legend(
    fig: plt.Figure,
    nodes: List[str],
    colors: Dict[str, str],
    *,
    vertical: bool = False,
    fontsize: float = 15.0,
    legend_x: float = 0.80,
    ncol: Optional[int] = None,
) -> None:
    """Add a color legend to *fig*."""
    handles = [
        mpatches.Patch(color=colors.get(n, "#CCCCCC"), label=n.replace("_", " "))
        for n in nodes
    ]
    if not handles:
        return
    if vertical:
        fig.legend(
            handles=handles, loc="center left", ncol=1,
            fontsize=fontsize, frameon=False, bbox_to_anchor=(legend_x, 0.5),
        )
    else:
        _ncol = ncol if ncol is not None else min(len(handles), 6)
        fig.legend(
            handles=handles, loc="lower center", ncol=_ncol,
            fontsize=fontsize, frameon=False, bbox_to_anchor=(0.5, 0.01),
        )


# ── Background ──────────────────────────────────────────────────

def _draw_background(
    ax: plt.Axes,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> None:
    if style.background_circles:
        for cx, cy, r, color in style.background_circles:
            ax.add_patch(plt.Circle((cx, cy), r, color=color, zorder=0))
        return
    if not pos:
        return
    max_dist = max(np.sqrt(x ** 2 + y ** 2) for x, y in pos.values())
    ax.add_patch(plt.Circle((0, 0), max_dist * 0.95, color=style.background_color, zorder=0))


# ── Nodes ────────────────────────────────────────────────────────

def _draw_node_circles(
    ax: plt.Axes,
    x: float, y: float, r: float,
    color: str, style: Style,
) -> None:
    ax.add_patch(plt.Circle(
        (x + style.shadow_offset, y - style.shadow_offset),
        r, color=style.shadow_color, zorder=2, ec="none",
    ))
    ax.add_patch(plt.Circle(
        (x, y), r, color=color, zorder=3,
        ec=style.node_edgecolor, lw=style.node_edgewidth,
    ))
    if style.highlight:
        hx = x - r * style.highlight_offset[0]
        hy = y + r * style.highlight_offset[1]
        ax.add_patch(plt.Circle(
            (hx, hy), r * style.highlight_radius_frac,
            color="white", alpha=style.highlight_alpha, zorder=4, ec="none",
        ))


def _draw_outer_label(
    ax: plt.Axes,
    x: float, y: float, r: float,
    label: str, style: Style,
    fontsize: Optional[float] = None,
) -> None:
    dist = np.sqrt(x ** 2 + y ** 2)
    ux, uy = (x / dist, y / dist) if dist > 1e-9 else (0.0, 1.0)
    lx = x + (r + style.label_offset) * ux
    ly = y + (r + style.label_offset) * uy
    if abs(ux) >= abs(uy):
        ha, va = ("left" if ux > 0 else "right"), "center"
    else:
        ha, va = "center", ("bottom" if uy > 0 else "top")
    text_obj = ax.text(
        lx, ly, label, ha=ha, va=va,
        fontsize=fontsize or style.label_fontsize,
        fontweight="bold", color=style.label_color, zorder=10,
    )
    if style.label_stroke_color is not None:
        text_obj.set_path_effects([
            mpe.withStroke(linewidth=style.label_stroke_width, foreground=style.label_stroke_color),
        ])


def _draw_nodes(
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> None:
    for name, node in graph.nodes.items():
        if name not in pos:
            continue
        x, y = pos[name]
        _draw_node_circles(ax, x, y, node.radius, node.color, style)
        label = node.display_label
        if node.label_position == "center":
            text_obj = ax.text(
                x, y, label, ha="center", va="center",
                fontsize=style.center_label_fontsize,
                fontweight="bold", color=style.center_label_color, zorder=10,
            )
            if style.label_stroke_color is not None:
                text_obj.set_path_effects([
                    mpe.withStroke(linewidth=style.label_stroke_width, foreground=style.label_stroke_color),
                ])
        else:
            _draw_outer_label(ax, x, y, node.radius, label, style)


# ── Edges ────────────────────────────────────────────────────────

def _draw_edges(
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

    weights = [e.weight for e in top]
    max_w, min_w = max(weights), min(weights)

    regular = [e for e in top if not e.is_self_loop]
    start_ang, end_ang = _compute_spread_angles(regular, pos, constrain_angles, style)

    for edge in top:
        if edge.source not in pos or edge.target not in pos:
            continue

        frac = (edge.weight - min_w) / (max_w - min_w + 1e-9)
        color = edge.color or style.edge_color(frac)
        lw = edge.linewidth or style.edge_linewidth(frac)
        alpha = edge.alpha or style.edge_alpha(frac)

        r_src = graph.nodes[edge.source].radius
        r_tgt = graph.nodes[edge.target].radius

        if edge.is_self_loop:
            _draw_self_loop(ax, pos[edge.source], r_src, color, lw, alpha, style)
        else:
            key = (edge.source, edge.target)
            sa = start_ang.get(key, _inward_angle(pos[edge.source]))
            ea = end_ang.get(key, _inward_angle(pos[edge.target]))
            _draw_arrow(ax, pos[edge.source], pos[edge.target],
                        r_src, r_tgt, sa, ea, color, lw, alpha, style)


# ── Angle helpers ────────────────────────────────────────────────

def _inward_angle(p: Tuple[float, float]) -> float:
    return float(np.arctan2(-p[1], -p[0]))


def _natural_angle(
    pos: Dict[str, Tuple[float, float]], node: str, partner: str,
) -> float:
    dx = pos[partner][0] - pos[node][0]
    dy = pos[partner][1] - pos[node][1]
    return float(np.arctan2(dy, dx))


def _compute_spread_angles(
    edges: list,
    pos: Dict[str, Tuple[float, float]],
    constrain: bool,
    style: Style,
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
    outgoing: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    incoming: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for e in edges:
        if e.source in pos and e.target in pos:
            outgoing[e.source].append((e.source, e.target))
            incoming[e.target].append((e.source, e.target))

    start: Dict[Tuple[str, str], float] = {}
    end: Dict[Tuple[str, str], float] = {}
    spread = style.arrow_spread_rad

    for node, out_edges in outgoing.items():
        center = _inward_angle(pos[node]) if constrain else None
        ordered = sorted(out_edges, key=lambda e: _natural_angle(pos, e[0], e[1]))
        n = len(ordered)
        for i, edge in enumerate(ordered):
            if constrain:
                offset = 0.0 if n == 1 else spread * (2 * i / (n - 1) - 1)
                start[edge] = center + offset  # type: ignore[operator]
            else:
                start[edge] = _natural_angle(pos, edge[0], edge[1])

    for node, in_edges in incoming.items():
        center = _inward_angle(pos[node]) if constrain else None
        ordered = sorted(in_edges, key=lambda e: _natural_angle(pos, e[1], e[0]))
        n = len(ordered)
        for i, edge in enumerate(ordered):
            if constrain:
                offset = 0.0 if n == 1 else spread * (2 * i / (n - 1) - 1)
                end[edge] = center + offset  # type: ignore[operator]
            else:
                end[edge] = _natural_angle(pos, edge[1], edge[0])

    return start, end


# ── Arrow / arrowhead / self-loop ────────────────────────────────

def _draw_arrow(
    ax: plt.Axes,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    r_start: float, r_end: float,
    start_ang: float, end_ang: float,
    color: str, lw: float, alpha: float,
    style: Style,
) -> None:
    start = (p1[0] + r_start * np.cos(start_ang),
             p1[1] + r_start * np.sin(start_ang))
    end = (p2[0] + r_end * np.cos(end_ang),
           p2[1] + r_end * np.sin(end_ang))

    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = np.sqrt(dx ** 2 + dy ** 2) + 1e-9
    px, py = -dy / dist, dx / dist

    ctrl = ((start[0] + end[0]) / 2 + px * style.curve_strength * dist,
            (start[1] + end[1]) / 2 + py * style.curve_strength * dist)

    ex, ey = end[0] - ctrl[0], end[1] - ctrl[1]
    ed = np.sqrt(ex ** 2 + ey ** 2) + 1e-9
    line_end = (end[0] - ex / ed * style.arrowhead_length,
                end[1] - ey / ed * style.arrowhead_length)

    ax.add_patch(mpatches.PathPatch(
        MplPath([start, ctrl, line_end], [MplPath.MOVETO, MplPath.CURVE3, MplPath.CURVE3]),
        facecolor="none", edgecolor=color, lw=lw, alpha=alpha, zorder=1,
    ))
    _draw_arrowhead(ax, end, ctrl, color, alpha, style)


def _draw_arrowhead(
    ax: plt.Axes,
    tip: Tuple[float, float],
    ctrl: Tuple[float, float],
    color: str, alpha: float,
    style: Style,
) -> None:
    tx, ty = tip[0] - ctrl[0], tip[1] - ctrl[1]
    td = np.sqrt(tx ** 2 + ty ** 2) + 1e-9
    tx, ty = tx / td, ty / td
    hl, hw = style.arrowhead_length, style.arrowhead_width
    base = (tip[0] - tx * hl, tip[1] - ty * hl)
    left = (base[0] + ty * hw / 2, base[1] - tx * hw / 2)
    right = (base[0] - ty * hw / 2, base[1] + tx * hw / 2)
    ax.add_patch(plt.Polygon(
        [tip, left, right], closed=True,
        color=color, alpha=alpha, zorder=5, ec="none",
    ))


def _draw_self_loop(
    ax: plt.Axes,
    pos_tuple: Tuple[float, float],
    node_r: float,
    color: str, lw: float, alpha: float,
    style: Style,
) -> None:
    x, y = pos_tuple
    dist = np.sqrt(x ** 2 + y ** 2)
    ux, uy = (x / dist, y / dist) if dist > 1e-9 else (0.0, 1.0)

    loop_r = node_r * style.self_loop_radius_frac
    cx = x + (node_r + loop_r) * ux
    cy = y + (node_r + loop_r) * uy

    attach_deg = np.degrees(np.arctan2(uy, ux)) + 180.0
    gap = style.self_loop_gap_deg
    theta1 = attach_deg + gap
    theta2 = attach_deg - gap + 360.0

    head_deg = np.degrees(style.arrowhead_length / loop_r)
    arc_end = theta2 - head_deg

    ax.add_patch(mpatches.Arc(
        (cx, cy), 2 * loop_r, 2 * loop_r,
        angle=0.0, theta1=theta1, theta2=arc_end,
        color=color, lw=lw, alpha=alpha, zorder=4,
    ))

    t2_rad = np.radians(theta2)
    t_before_rad = np.radians(arc_end - 10.0)
    tip = (cx + loop_r * np.cos(t2_rad), cy + loop_r * np.sin(t2_rad))
    ctrl = (cx + loop_r * np.cos(t_before_rad), cy + loop_r * np.sin(t_before_rad))
    _draw_arrowhead(ax, tip, ctrl, color, alpha, style)


# ── Axes / title ─────────────────────────────────────────────────

def _finalize_axes(
    ax: plt.Axes,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> None:
    if not pos:
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
    else:
        node_lim = max(max(abs(x), abs(y)) for x, y in pos.values())
        bg_lim = (
            max((abs(cy) + r for _, cy, r, _ in style.background_circles), default=0.0)
            if style.fit_background_circles and style.background_circles
            else 0.0
        )
        lim = max(node_lim, bg_lim) + style.axis_margin
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
    ax.axis("off")
    ax.set_aspect("equal")


def _compute_content_top(
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> float:
    if style.background_circles:
        return max(cy + r for _, cy, r, _ in style.background_circles)
    if pos:
        return max(abs(y) for _, y in pos.values())
    return 1.0


def _draw_title(
    ax: plt.Axes,
    title: str, subtitle: str,
    style: Style,
    content_top: float,
) -> None:
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_frac = (content_top - ylim[0]) / (ylim[1] - ylim[0])
    dpi_trans = ax.figure.dpi_scale_trans
    subtitle_fs = style.title_fontsize * style.subtitle_fontsize_ratio

    sub_pt = style.subtitle_pad
    title_pt = sub_pt + subtitle_fs * 1.2 + 2.0

    if subtitle:
        sub_trans = (
            ax.transAxes
            + ScaledTranslation(0, sub_pt / 72, dpi_trans)
        )
        ax.text(
            0.5, y_frac, subtitle, transform=sub_trans,
            ha="center", va="bottom", clip_on=False,
            fontsize=subtitle_fs, fontweight="normal",
        )
    if title:
        title_pt_final = title_pt if subtitle else sub_pt
        title_trans = (
            ax.transAxes
            + ScaledTranslation(0, title_pt_final / 72, dpi_trans)
        )
        ax.text(
            0.5, y_frac, title, transform=title_trans,
            ha="center", va="bottom", clip_on=False,
            fontsize=style.title_fontsize, fontweight="bold",
        )
