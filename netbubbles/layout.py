"""Layout algorithms for positioning nodes."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np


def circular(
    nodes: List[str],
    *,
    radius: float = 2.59,
    start_angle: float = np.pi / 2,
    order: Optional[List[str]] = None,
) -> Dict[str, Tuple[float, float]]:
    """Place nodes evenly around a circle."""
    if order is not None:
        present = set(nodes)
        ordered = [n for n in order if n in present]
        for n in nodes:
            if n not in ordered:
                ordered.append(n)
    else:
        ordered = sorted(nodes)

    count = len(ordered)
    angles = [start_angle + 2 * np.pi * i / count for i in range(count)]
    return {
        n: (float(radius * np.cos(a)), float(radius * np.sin(a)))
        for n, a in zip(ordered, angles)
    }


def bilayer(
    inner_nodes: List[str],
    outer_nodes: List[str],
    *,
    inner_radius: float = 0.60,
    outer_radius: float = 1.50,
) -> Dict[str, Tuple[float, float]]:
    """Two concentric rings: inner group and outer group."""
    pos: Dict[str, Tuple[float, float]] = {}
    for i, node in enumerate(sorted(inner_nodes)):
        angle = 2 * np.pi * i / max(len(inner_nodes), 1)
        pos[node] = (float(inner_radius * np.cos(angle)),
                     float(inner_radius * np.sin(angle)))
    for i, node in enumerate(sorted(outer_nodes)):
        angle = 2 * np.pi * i / max(len(outer_nodes), 1)
        pos[node] = (float(outer_radius * np.cos(angle)),
                     float(outer_radius * np.sin(angle)))
    return pos


def focus(
    nodes: List[str],
    center: str,
    *,
    ring_radius: float = 2.59,
    order: Optional[List[str]] = None,
) -> Dict[str, Tuple[float, float]]:
    """One node in the center, the rest on a ring around it."""
    pos: Dict[str, Tuple[float, float]] = {center: (0.0, 0.0)}
    others = [n for n in nodes if n != center]
    if others:
        pos.update(circular(others, radius=ring_radius, order=order))
    return pos


def grid(
    nodes: List[str],
    *,
    spacing: float = 2.5,
) -> Dict[str, Tuple[float, float]]:
    """Regular grid layout."""
    n = len(nodes)
    cols = int(np.ceil(np.sqrt(n)))
    pos: Dict[str, Tuple[float, float]] = {}
    for i, node in enumerate(nodes):
        row, col = divmod(i, cols)
        pos[node] = (col * spacing, -row * spacing)
    return pos


def manual(
    positions: Dict[str, Tuple[float, float]],
) -> Dict[str, Tuple[float, float]]:
    """Pass-through for user-supplied positions."""
    return dict(positions)
