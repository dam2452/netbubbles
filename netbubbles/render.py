"""Render a BubbleGraph onto matplotlib axes."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

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
    _finalize_axes(ax, pos, style)
    if background:
        _draw_background(ax, pos, style)
    border_half = _node_border_half_data(ax, style)
    _draw_edges(ax, graph, pos, style, constrain_angles, border_half)
    _draw_nodes(ax, graph, pos, style)
    content_top = _compute_content_top(ax, graph, pos, style)
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
    ncol: Optional[Union[int, str]] = None,
) -> None:
    """Add a color legend to *fig*.

    ncol variants:
      None       — auto: fit within 150 % of figure width
      int        — fixed number of columns
      "NxM"      — N columns, at most M items per column (clips handles list)
    """
    labels = [n.replace("_", " ") for n in nodes]
    handles = [mpatches.Patch(color=colors.get(n, "#CCCCCC"), label=lbl)
               for n, lbl in zip(nodes, labels)]
    if not handles:
        return

    if vertical:
        fig.legend(
            handles=handles, loc="center left", ncol=1,
            fontsize=fontsize, frameon=False, bbox_to_anchor=(legend_x, 0.5),
        )
        return

    _ncol, handles = _resolve_ncol(ncol, handles, labels, fontsize, fig)
    fig.legend(
        handles=handles, loc="lower center", ncol=_ncol,
        fontsize=fontsize, frameon=False, bbox_to_anchor=(0.5, 0.01),
    )


def _resolve_ncol(
    ncol: Optional[Union[int, str]],
    handles: list,
    labels: List[str],
    fontsize: float,
    fig: plt.Figure,
) -> Tuple[int, list]:
    if isinstance(ncol, str):
        parts = ncol.lower().split("x")
        if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
            raise ValueError(f"ncol string must be 'NxM', got: {ncol!r}")
        cols, per_col = int(parts[0]), int(parts[1])
        return cols, handles[: cols * per_col]

    if isinstance(ncol, int):
        return ncol, handles

    # auto: estimate item width in points, fit within 125% of figure width
    fig_width_pt = fig.get_figwidth() * 72.0
    max_legend_pt = fig_width_pt * 1.25
    handle_pt = 30.0  # patch + gap
    char_pt = fontsize * 0.55
    max_label_len = max((len(lbl) for lbl in labels), default=1)
    item_pt = handle_pt + max_label_len * char_pt
    auto_ncol = max(1, min(len(handles), int(max_legend_pt / item_pt)))
    return _balance_ncol(auto_ncol, len(handles)), handles


def _balance_ncol(max_ncol: int, n: int) -> int:
    initial_waste = (-n) % max_ncol if max_ncol else 0
    if initial_waste < max_ncol / 3:
        return max_ncol
    min_ncol = max(1, int(max_ncol * 0.75))
    best_ncol, best_waste = max_ncol, initial_waste
    for c in range(max_ncol - 1, min_ncol - 1, -1):
        waste = (-n) % c
        if waste < best_waste:
            best_waste, best_ncol = waste, c
        if best_waste == 0:
            break
    return best_ncol


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


def _label_placement(
    x: float, y: float, r: float,
    angle_offset: float,
    label_offset: float,
) -> Tuple[float, float, str, str]:
    """Return (lx, ly, ha, va) for an outer label at node (x, y).

    angle_offset nudges the label angle to separate crowded neighbours.
    ha/va are chosen from 9 directions based on the final angle so the text
    anchor always points away from the node — no text ever sits on top of its
    own bubble.
    """
    base_angle = float(np.arctan2(y, x)) if (abs(x) + abs(y)) > 1e-9 else np.pi / 2
    angle = base_angle + angle_offset
    ux, uy = float(np.cos(angle)), float(np.sin(angle))
    lx = x + (r + label_offset) * ux
    ly = y + (r + label_offset) * uy

    cos_thresh = 0.35
    if ux > cos_thresh:
        ha = "left"
    elif ux < -cos_thresh:
        ha = "right"
    else:
        ha = "center"

    if uy > cos_thresh:
        va = "bottom"
    elif uy < -cos_thresh:
        va = "top"
    else:
        va = "center"

    return lx, ly, ha, va


def _compute_angle_offsets(
    pos: Dict[str, List[str]],
    node_names: List[str],
    min_sep_rad: float = float(np.radians(18.0)),
) -> Dict[str, float]:
    """Push apart labels for nodes whose outward angles are too close.

    Iterates pairs sorted by angular distance; for each pair that is closer
    than min_sep_rad, nudges both in opposite directions just enough to reach
    the minimum separation.  Returns a dict of name -> angle_offset (radians).
    """
    angles = {}
    for name in node_names:
        if name not in pos:
            continue
        x, y = pos[name]
        angles[name] = float(np.arctan2(y, x)) if (abs(x) + abs(y)) > 1e-9 else np.pi / 2

    offsets: Dict[str, float] = {n: 0.0 for n in angles}

    names = list(angles.keys())
    for _ in range(6):
        moved = False
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                da = ((angles[a] + offsets[a]) - (angles[b] + offsets[b]) + np.pi) % (2 * np.pi) - np.pi
                if abs(da) < min_sep_rad:
                    push = (min_sep_rad - abs(da)) / 2.0 * np.sign(da) if da != 0 else min_sep_rad / 2.0
                    offsets[a] += push
                    offsets[b] -= push
                    moved = True
        if not moved:
            break

    return offsets


def _place_label(
    ax: plt.Axes,
    x: float, y: float, r: float,
    label: str, style: Style,
    angle_offset: float = 0.0,
    fontsize: Optional[float] = None,
) -> None:
    lx, ly, ha, va = _label_placement(x, y, r, angle_offset, style.label_offset)
    text_obj = ax.text(
        lx, ly, label, ha=ha, va=va,
        fontsize=fontsize or style.label_fontsize,
        fontweight="bold", color=style.label_color, zorder=10,
    )
    if style.label_stroke_color is not None:
        text_obj.set_path_effects([
            mpe.withStroke(linewidth=style.label_stroke_width,
                           foreground=style.label_stroke_color),
        ])


def _draw_nodes(
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> None:
    outer_names = [
        n for n, node in graph.nodes.items()
        if n in pos and node.label_position != "center"
    ]
    min_sep = float(np.radians(style.label_min_sep_deg))
    angle_offsets = _compute_angle_offsets(pos, outer_names, min_sep_rad=min_sep)  # type: ignore[arg-type]

    for name, node in graph.nodes.items():
        if name not in pos:
            continue
        x, y = pos[name]
        _draw_node_circles(ax, x, y, node.radius, node.color, style)
        label = node.display_label
        if node.label_position == "center":
            text_obj = ax.text(
                x, y, label, ha="center", va="center",
                fontsize=node.label_fontsize if node.label_fontsize is not None else style.center_label_fontsize,
                fontweight="bold", color=style.center_label_color, zorder=10,
            )
            if style.label_stroke_color is not None:
                text_obj.set_path_effects([
                    mpe.withStroke(linewidth=style.label_stroke_width,
                                   foreground=style.label_stroke_color),
                ])
        else:
            _place_label(ax, x, y, node.radius, label, style,
                         angle_offset=angle_offsets.get(name, 0.0),
                         fontsize=node.label_fontsize)


# ── Edges ────────────────────────────────────────────────────────

def _node_border_half_data(ax: plt.Axes, style: Style) -> float:
    """Return half of node_edgewidth converted from points to data units."""
    dpi = ax.figure.dpi
    border_px = style.node_edgewidth / 2.0 * dpi / 72.0
    inv = ax.transData.inverted()
    p0 = inv.transform((0.0, 0.0))
    p1 = inv.transform((0.0, border_px))
    return float(abs(p1[1] - p0[1]))


def _draw_edges(
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
    constrain_angles: bool,
    border_half: float,
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
    bow_signs = _compute_bow_signs(regular, pos)

    for edge in top:
        if edge.source not in pos or edge.target not in pos:
            continue

        frac = (edge.weight - min_w) / (max_w - min_w + 1e-9)
        color = edge.color or style.edge_color(frac)
        lw = edge.linewidth or style.edge_linewidth(frac)
        alpha = edge.alpha or style.edge_alpha(frac)

        r_src = graph.nodes[edge.source].radius + (border_half if style.arrow_tail_hugs_border else 0.0)
        r_tgt = graph.nodes[edge.target].radius + border_half

        if edge.is_self_loop:
            _draw_self_loop(ax, pos[edge.source], r_src, color, lw, alpha, style)
        else:
            key = (edge.source, edge.target)
            sa = start_ang.get(key, _inward_angle(pos[edge.source]))
            ea = end_ang.get(key, _inward_angle(pos[edge.target]))
            bow = bow_signs.get(key, 1.0)
            _draw_arrow(ax, pos[edge.source], pos[edge.target],
                        r_src, r_tgt, sa, ea, bow, color, lw, alpha, style)


# ── Angle helpers ────────────────────────────────────────────────

def _inward_angle(p: Tuple[float, float]) -> float:
    return float(np.arctan2(-p[1], -p[0]))


def _mean_angle(angles: List[float]) -> float:
    return float(np.arctan2(np.mean(np.sin(angles)), np.mean(np.cos(angles))))


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

    # seed every edge with its natural angle first
    for e in edges:
        if e.source in pos and e.target in pos:
            key = (e.source, e.target)
            start[key] = _natural_angle(pos, e.source, e.target)
            end[key]   = _natural_angle(pos, e.target, e.source)

    if not constrain:
        return start, end

    # per node: sort ALL touching edges together by natural angle, then nudge
    # only those that are too close — preserves natural paths, avoids heavy deflection
    min_gap = style.arrow_spread_rad
    all_nodes = set(outgoing) | set(incoming)
    for node in all_nodes:
        entries: List[Tuple[float, str, Tuple[str, str]]] = []
        for edge in outgoing.get(node, []):
            entries.append((_natural_angle(pos, edge[0], edge[1]), "out", edge))
        for edge in incoming.get(node, []):
            entries.append((_natural_angle(pos, edge[1], edge[0]), "in", edge))

        if len(entries) < 2:
            continue

        entries.sort(key=lambda x: x[0])
        adjusted = [a for a, _, _ in entries]

        for _ in range(30):
            moved = False
            for i in range(len(adjusted) - 1):
                gap = adjusted[i + 1] - adjusted[i]
                if gap < min_gap:
                    push = (min_gap - gap) / 2.0
                    adjusted[i] -= push
                    adjusted[i + 1] += push
                    moved = True
            if not moved:
                break

        for i, (_, direction, edge) in enumerate(entries):
            if direction == "out":
                start[edge] = adjusted[i]
            else:
                end[edge] = adjusted[i]

    return start, end


def _compute_bow_signs(
    edges: list,
    pos: Dict[str, Tuple[float, float]],
) -> Dict[Tuple[str, str], float]:
    """Return +1 / -1 bow sign per edge to separate crossing arc pairs.

    For each pair of edges whose straight-line chords cross and that share no
    node, assign opposite bow directions so their bezier arcs diverge.
    """
    valid = [(e.source, e.target) for e in edges
             if e.source in pos and e.target in pos]
    signs: Dict[Tuple[str, str], float] = {k: 1.0 for k in valid}

    def _cross2d(ox: float, oy: float, ax: float, ay: float, bx: float, by: float) -> float:
        return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

    def _chords_cross(a: Tuple[float, float], b: Tuple[float, float],
                      c: Tuple[float, float], d: Tuple[float, float]) -> bool:
        d1 = _cross2d(c[0], c[1], d[0], d[1], a[0], a[1])
        d2 = _cross2d(c[0], c[1], d[0], d[1], b[0], b[1])
        d3 = _cross2d(a[0], a[1], b[0], b[1], c[0], c[1])
        d4 = _cross2d(a[0], a[1], b[0], b[1], d[0], d[1])
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    for i in range(len(valid)):
        k1 = valid[i]
        for j in range(i + 1, len(valid)):
            k2 = valid[j]
            if k1[0] in k2 or k1[1] in k2:
                continue
            if _chords_cross(pos[k1[0]], pos[k1[1]], pos[k2[0]], pos[k2[1]]):
                if signs[k1] == signs[k2]:
                    signs[k2] = -signs[k2]

    return signs


# ── Arrow / arrowhead / self-loop ────────────────────────────────

def _draw_arrow(
    ax: plt.Axes,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    r_start: float, r_end: float,
    start_ang: float, end_ang: float,
    bow_sign: float,
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

    ctrl = ((start[0] + end[0]) / 2 + bow_sign * px * style.curve_strength * dist,
            (start[1] + end[1]) / 2 + bow_sign * py * style.curve_strength * dist)

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
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> float:
    if style.background_circles:
        base = max(cy + r for _, cy, r, _ in style.background_circles)
    elif pos:
        base = max(
            y + graph.nodes[name].radius
            for name, (_, y) in pos.items()
            if name in graph.nodes
        )
    else:
        return 1.0

    ylim = ax.get_ylim()
    fig_height_pt = ax.get_figure().get_figheight() * 72.0
    ax_height_frac = ax.get_position().height
    pts_per_data_unit = (fig_height_pt * ax_height_frac) / (ylim[1] - ylim[0])

    top = base
    self_loop_nodes = {e.source for e in graph.edges if e.is_self_loop}

    for name, node in graph.nodes.items():
        if name not in pos:
            continue
        x, y = pos[name]
        dist = np.sqrt(x ** 2 + y ** 2)
        ux, uy = (x / dist, y / dist) if dist > 1e-9 else (0.0, 1.0)

        if node.label_position != "center" and uy > 0 and abs(uy) >= abs(ux):
            fs = node.label_fontsize if node.label_fontsize is not None else style.label_fontsize
            label_base_y = y + (node.radius + style.label_offset) * uy
            top = max(top, label_base_y + fs * 1.2 / pts_per_data_unit)

        if name in self_loop_nodes and uy > 0:
            loop_r = node.radius * style.self_loop_radius_frac
            loop_cy = y + (node.radius + loop_r) * uy
            top = max(top, loop_cy + loop_r)

    return top


def _draw_title(
    ax: plt.Axes,
    title: str, subtitle: str,
    style: Style,
    content_top: float,
) -> None:
    ylim = ax.get_ylim()
    y_frac = (content_top - ylim[0]) / (ylim[1] - ylim[0])
    dpi_trans = ax.figure.dpi_scale_trans
    subtitle_fs = style.title_fontsize * style.subtitle_fontsize_ratio

    # title sits title_pad pts above content_top
    # subtitle sits subtitle_pad pts below the title (close to it)
    title_offset_pt = style.title_pad
    sub_offset_pt = style.title_pad - subtitle_fs * 1.2 - style.subtitle_pad

    if subtitle:
        ax.text(
            0.5, y_frac, subtitle,
            transform=ax.transAxes + ScaledTranslation(0, sub_offset_pt / 72, dpi_trans),
            ha="center", va="bottom", clip_on=False,
            fontsize=subtitle_fs, fontweight="normal",
        )
    if title:
        ax.text(
            0.5, y_frac, title,
            transform=ax.transAxes + ScaledTranslation(0, title_offset_pt / 72, dpi_trans),
            ha="center", va="bottom", clip_on=False,
            fontsize=style.title_fontsize, fontweight="bold",
        )
