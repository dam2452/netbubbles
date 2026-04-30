"""Arrow, arrowhead, and self-loop drawing primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import matplotlib.patches as mpatches
from matplotlib.path import Path as MplPath
import matplotlib.pyplot as plt
import numpy as np

from ..style import Style


@dataclass
class _ArrowGeometry:
    start: Tuple[float, float]
    ctrl: Tuple[float, float]
    line_end: Tuple[float, float]
    tip: Tuple[float, float]


def _bezier_ctrl(
    start: Tuple[float, float],
    end: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    bow_sign: float,
    curve_strength: float,
    bg_radius: float,
    is_bidirectional: bool,
) -> Tuple[float, float]:
    mx = (start[0] + end[0]) / 2.0
    my = (start[1] + end[1]) / 2.0
    r1 = np.sqrt(p1[0] ** 2 + p1[1] ** 2) + 1e-9
    r2 = np.sqrt(p2[0] ** 2 + p2[1] ** 2) + 1e-9
    cos_angle = np.clip((p1[0] * p2[0] + p1[1] * p2[1]) / (r1 * r2), -1.0, 1.0)
    closeness = (1.0 + cos_angle) / 2.0
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = np.sqrt(dx ** 2 + dy ** 2) + 1e-9
    px, py = -dy / dist, dx / dist
    if is_bidirectional:
        bow_factor = 0.45 * closeness + 0.12
        cx = mx + bow_sign * px * bow_factor * dist
        cy = my + bow_sign * py * bow_factor * dist
    else:
        dynamic_pull = max(0.05, curve_strength * 0.4 * closeness)
        cx = mx * (1.0 - dynamic_pull)
        cy = my * (1.0 - dynamic_pull)
        bow_factor = 0.12 * closeness + 0.04
        cx += bow_sign * px * bow_factor * dist
        cy += bow_sign * py * bow_factor * dist
    cd = np.sqrt(cx ** 2 + cy ** 2)
    if cd > bg_radius:
        cx, cy = cx * bg_radius / cd, cy * bg_radius / cd
    return (cx, cy)


def _line_end_before_tip(
    end: Tuple[float, float],
    ctrl: Tuple[float, float],
    arrowhead_length: float,
) -> Tuple[float, float]:
    ex, ey = end[0] - ctrl[0], end[1] - ctrl[1]
    ed = np.sqrt(ex ** 2 + ey ** 2) + 1e-9
    return (end[0] - ex / ed * arrowhead_length, end[1] - ey / ed * arrowhead_length)


def _compute_arrow_geometry(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    r_start: float, r_end: float,
    start_ang: float, end_ang: float,
    bow_sign: float,
    bg_radius: float,
    curve_strength: float,
    arrowhead_length: float,
    is_bidirectional: bool,
) -> _ArrowGeometry:
    start = (p1[0] + r_start * np.cos(start_ang), p1[1] + r_start * np.sin(start_ang))
    end = (p2[0] + r_end * np.cos(end_ang), p2[1] + r_end * np.sin(end_ang))
    ctrl = _bezier_ctrl(start, end, p1, p2, bow_sign, curve_strength, bg_radius, is_bidirectional)
    line_end = _line_end_before_tip(end, ctrl, arrowhead_length)
    return _ArrowGeometry(start=start, ctrl=ctrl, line_end=line_end, tip=end)


@dataclass
class _SelfLoopGeometry:
    center: Tuple[float, float]
    loop_r: float
    theta1: float
    arc_end: float


def _compute_self_loop_geometry(
    pos_tuple: Tuple[float, float],
    node_r: float,
    self_loop_radius_frac: float,
    self_loop_gap_deg: float,
    arrowhead_length: float,
) -> _SelfLoopGeometry:
    x, y = pos_tuple
    dist = np.sqrt(x ** 2 + y ** 2)
    ux, uy = (x / dist, y / dist) if dist > 1e-9 else (0.0, 1.0)

    loop_r = node_r * self_loop_radius_frac
    cx = x + (node_r + loop_r) * ux
    cy = y + (node_r + loop_r) * uy

    attach_deg = np.degrees(np.arctan2(uy, ux)) + 180.0
    theta1 = attach_deg + self_loop_gap_deg
    theta2 = attach_deg - self_loop_gap_deg + 360.0
    arc_end = theta2 - np.degrees(arrowhead_length / loop_r)

    return _SelfLoopGeometry(center=(cx, cy), loop_r=loop_r, theta1=theta1, arc_end=arc_end)


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
    ax.add_patch(
        plt.Polygon(
            [tip, left, right], closed=True,
            color=color, alpha=alpha, zorder=5, ec="none",
        ),
    )


def draw_arrow(  # pylint: disable=too-many-arguments
    ax: plt.Axes,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    r_start: float, r_end: float,
    start_ang: float, end_ang: float,
    bow_sign: float,
    bg_radius: float,
    color: str, lw: float, alpha: float,
    style: Style,
    is_bidirectional: bool = False,
) -> None:
    geom = _compute_arrow_geometry(
        p1, p2, r_start, r_end, start_ang, end_ang, bow_sign, bg_radius,
        style.curve_strength, style.arrowhead_length, is_bidirectional,
    )
    ax.add_patch(
        mpatches.PathPatch(
            MplPath(
                [geom.start, geom.ctrl, geom.line_end],
                [MplPath.MOVETO, MplPath.CURVE3, MplPath.CURVE3],
            ),
            facecolor="none", edgecolor=color, lw=lw, alpha=alpha, zorder=1,
        ),
    )
    _draw_arrowhead(ax, geom.tip, geom.ctrl, color, alpha, style)


def draw_self_loop(
    ax: plt.Axes,
    pos_tuple: Tuple[float, float],
    node_r: float,
    color: str, lw: float, alpha: float,
    style: Style,
) -> None:
    geom = _compute_self_loop_geometry(
        pos_tuple, node_r,
        style.self_loop_radius_frac, style.self_loop_gap_deg, style.arrowhead_length,
    )
    cx, cy = geom.center
    ax.add_patch(
        mpatches.Arc(
            (cx, cy), 2 * geom.loop_r, 2 * geom.loop_r,
            angle=0.0, theta1=geom.theta1, theta2=geom.arc_end,
            color=color, lw=lw, alpha=alpha, zorder=4,
        ),
    )

    arc_end_rad = np.radians(geom.arc_end)
    tan_x = -np.sin(arc_end_rad)
    tan_y = np.cos(arc_end_rad)
    base = (cx + geom.loop_r * np.cos(arc_end_rad), cy + geom.loop_r * np.sin(arc_end_rad))
    tip = (base[0] + tan_x * style.arrowhead_length, base[1] + tan_y * style.arrowhead_length)
    fake_ctrl = (base[0] - tan_x * 0.001, base[1] - tan_y * 0.001)
    _draw_arrowhead(ax, tip, fake_ctrl, color, alpha, style)
