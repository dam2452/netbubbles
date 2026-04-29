"""Node circle and label drawing."""

from __future__ import annotations

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import matplotlib.patheffects as mpe
import matplotlib.pyplot as plt
import numpy as np

from ..graph import BubbleGraph
from ..style import Style


def node_border_half_data(ax: plt.Axes, style: Style) -> float:
    """Return half of node_edgewidth converted from points to data units."""
    dpi = ax.figure.dpi
    border_px = style.node_edgewidth / 2.0 * dpi / 72.0
    inv = ax.transData.inverted()
    p0 = inv.transform((0.0, 0.0))
    p1 = inv.transform((0.0, border_px))
    return float(abs(p1[1] - p0[1]))


def draw_node_circles(
    ax: plt.Axes,
    x: float, y: float, r: float,
    color: str, style: Style,
) -> None:
    ax.add_patch(
        plt.Circle(
            (x + style.shadow_offset, y - style.shadow_offset),
            r, color=style.shadow_color, zorder=2, ec="none",
        ),
    )
    ax.add_patch(
        plt.Circle(
            (x, y), r, color=color, zorder=3,
            ec=style.node_edgecolor, lw=style.node_edgewidth,
        ),
    )
    if style.highlight:
        hx = x - r * style.highlight_offset[0]
        hy = y + r * style.highlight_offset[1]
        ax.add_patch(
            plt.Circle(
                (hx, hy), r * style.highlight_radius_frac,
                color="white", alpha=style.highlight_alpha, zorder=4, ec="none",
            ),
        )


def label_placement(
    x: float, y: float, r: float,
    angle_offset: float,
    label_offset: float,
) -> Tuple[float, float, str, str]:
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


def compute_angle_offsets(
    pos: Dict[str, Tuple[float, float]],
    node_names: List[str],
    min_sep_rad: float = float(np.radians(18.0)),
) -> Dict[str, float]:
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
        for i in range(len(names)):  # pylint: disable=consider-using-enumerate
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


def _apply_stroke(text_obj: plt.Text, style: Style) -> None:
    if style.label_stroke_color is not None:
        text_obj.set_path_effects([
            mpe.withStroke(
                linewidth=style.label_stroke_width,
                foreground=style.label_stroke_color,
            ),
        ])


def place_label(
    ax: plt.Axes,
    x: float, y: float, r: float,
    label: str, style: Style,
    angle_offset: float = 0.0,
    fontsize: Optional[float] = None,
) -> None:
    lx, ly, ha, va = label_placement(x, y, r, angle_offset, style.label_offset)
    text_obj = ax.text(
        lx, ly, label, ha=ha, va=va,
        fontsize=fontsize or style.label_fontsize,
        fontweight="bold", color=style.label_color, zorder=10,
    )
    _apply_stroke(text_obj, style)


def draw_nodes(
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
    angle_offsets = compute_angle_offsets(pos, outer_names, min_sep_rad=min_sep)  # type: ignore[arg-type]

    for name, node in graph.nodes.items():
        if name not in pos:
            continue
        x, y = pos[name]
        draw_node_circles(ax, x, y, node.radius, node.color, style)
        label = node.display_label
        if node.label_position == "center":
            text_obj = ax.text(
                x, y, label, ha="center", va="center",
                fontsize=node.label_fontsize if node.label_fontsize is not None else style.center_label_fontsize,
                fontweight="bold", color=style.center_label_color, zorder=10,
            )
            _apply_stroke(text_obj, style)
        else:
            place_label(
                ax, x, y, node.radius, label, style,
                angle_offset=angle_offsets.get(name, 0.0),
                fontsize=node.label_fontsize,
            )
