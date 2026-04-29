"""Title and subtitle drawing, content-top computation."""

from __future__ import annotations

from typing import (
    Dict,
    Tuple,
)

import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
import numpy as np

from ..graph import BubbleGraph
from ..style import Style


def _pts_per_data_unit(ax: plt.Axes) -> float:
    ylim = ax.get_ylim()
    fig_height_pt = ax.get_figure().get_figheight() * 72.0
    ax_height_frac = ax.get_position().height
    return (fig_height_pt * ax_height_frac) / (ylim[1] - ylim[0])


def _content_base(
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> float:
    if style.background_circles:
        return max(cy + r for _, cy, r, _ in style.background_circles)
    if pos:
        return max(
            y + graph.nodes[name].radius
            for name, (_, y) in pos.items()
            if name in graph.nodes
        )
    return 1.0


def compute_content_top(
    ax: plt.Axes,
    graph: BubbleGraph,
    pos: Dict[str, Tuple[float, float]],
    style: Style,
) -> float:
    if not style.background_circles and not pos:
        return 1.0

    top = _content_base(graph, pos, style)
    scale = _pts_per_data_unit(ax)
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
            top = max(top, label_base_y + fs * 1.2 / scale)

        if name in self_loop_nodes and uy > 0:
            loop_r = node.radius * style.self_loop_radius_frac
            loop_cy = y + (node.radius + loop_r) * uy
            top = max(top, loop_cy + loop_r)

    return top


def draw_title(
    ax: plt.Axes,
    title: str, subtitle: str,
    style: Style,
    content_top: float,
) -> None:
    ylim = ax.get_ylim()
    y_frac = (content_top - ylim[0]) / (ylim[1] - ylim[0])
    dpi_trans = ax.figure.dpi_scale_trans
    subtitle_fs = style.title_fontsize * style.subtitle_fontsize_ratio

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
