"""Pure geometric helpers: angles, arc spreading, bow signs."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    Dict,
    List,
    Tuple,
)

import numpy as np


def inward_angle(p: Tuple[float, float]) -> float:
    return float(np.arctan2(-p[1], -p[0]))


def _clamp_to_arc(angle: float, center: float, limit: float) -> float:
    diff = (angle - center + np.pi) % (2 * np.pi) - np.pi
    clamped = np.clip(diff, -limit, limit)
    return float((center + clamped + np.pi) % (2 * np.pi) - np.pi)


def mean_angle(angles: List[float]) -> float:
    return float(np.arctan2(np.mean(np.sin(angles)), np.mean(np.cos(angles))))


def natural_angle(
    pos: Dict[str, Tuple[float, float]], node: str, partner: str,
) -> float:
    dx = pos[partner][0] - pos[node][0]
    dy = pos[partner][1] - pos[node][1]
    return float(np.arctan2(dy, dx))


def _relax_angles(values: List[float], min_gap: float, max_iter: int = 30) -> List[float]:
    result = list(values)
    for _ in range(max_iter):
        moved = False
        for i in range(len(result) - 1):
            gap = result[i + 1] - result[i]
            if gap < min_gap:
                push = (min_gap - gap) / 2.0
                result[i] -= push
                result[i + 1] += push
                moved = True
        if not moved:
            break
    return result


def compute_spread_angles(
    edges: list,
    pos: Dict[str, Tuple[float, float]],
    constrain: bool,
    arrow_spread_rad: float,
    arrow_arc_limit_rad: float = float(np.pi),
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
    outgoing: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    incoming: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for e in edges:
        if e.source in pos and e.target in pos:
            outgoing[e.source].append((e.source, e.target))
            incoming[e.target].append((e.source, e.target))

    start: Dict[Tuple[str, str], float] = {}
    end: Dict[Tuple[str, str], float] = {}

    for e in edges:
        if e.source in pos and e.target in pos:
            key = (e.source, e.target)
            start[key] = inward_angle(pos[e.source])
            end[key] = inward_angle(pos[e.target])

    if not constrain:
        return start, end

    all_nodes = set(outgoing) | set(incoming)
    for node in all_nodes:
        inward = inward_angle(pos[node])

        out_edges = outgoing.get(node, [])
        in_edges = incoming.get(node, [])
        all_edges: List[Tuple[str, Tuple[str, str]]] = (
            [("out", e) for e in out_edges] + [("in", e) for e in in_edges]
        )
        if len(all_edges) < 2:
            continue

        def _nat(item: Tuple[str, Tuple[str, str]]) -> float:
            direction, edge = item
            return natural_angle(pos, edge[0], edge[1]) if direction == "out" else natural_angle(pos, edge[1], edge[0])

        def _sort_key(item: Tuple[str, Tuple[str, str]]) -> float:
            diff = (_nat(item) - inward + np.pi) % (2 * np.pi) - np.pi
            return float(diff)

        all_edges.sort(key=_sort_key)
        n = len(all_edges)
        half = (n - 1) / 2.0
        for i, (direction, edge) in enumerate(all_edges):
            offset = (i - half) * arrow_spread_rad
            angle = _clamp_to_arc(inward + offset, inward, arrow_arc_limit_rad)
            if direction == "out":
                start[edge] = angle
            else:
                end[edge] = angle

    return start, end


def compute_bow_signs(
    edges: list,
    pos: Dict[str, Tuple[float, float]],
) -> Dict[Tuple[str, str], float]:
    valid = [
        (e.source, e.target) for e in edges
        if e.source in pos and e.target in pos
    ]
    signs: Dict[Tuple[str, str], float] = {k: 1.0 for k in valid}

    def _cross2d(ox: float, oy: float, ax: float, ay: float, bx: float, by: float) -> float:
        return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

    def _chords_cross(
        a: Tuple[float, float], b: Tuple[float, float],
        c: Tuple[float, float], d: Tuple[float, float],
    ) -> bool:
        d1 = _cross2d(c[0], c[1], d[0], d[1], a[0], a[1])
        d2 = _cross2d(c[0], c[1], d[0], d[1], b[0], b[1])
        d3 = _cross2d(a[0], a[1], b[0], b[1], c[0], c[1])
        d4 = _cross2d(a[0], a[1], b[0], b[1], d[0], d[1])
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    for i in range(len(valid)):  # pylint: disable=consider-using-enumerate
        k1 = valid[i]
        rev1 = (k1[1], k1[0])
        for j in range(i + 1, len(valid)):
            k2 = valid[j]
            if k2 == rev1:
                continue
            if k1[0] in k2 or k1[1] in k2:
                continue
            if _chords_cross(pos[k1[0]], pos[k1[1]], pos[k2[0]], pos[k2[1]]):
                if signs[k1] == signs[k2]:
                    signs[k2] = -signs[k2]

    for k in list(signs):
        rev = (k[1], k[0])
        if rev in signs and k < rev:
            signs[rev] = -signs[k]

    return signs
