"""Background circle and axes finalization."""

from __future__ import annotations

from typing import (
    Dict,
    Tuple,
)

import matplotlib.pyplot as plt
import numpy as np

from ..style import Style


def draw_background(
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


def finalize_axes(
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
