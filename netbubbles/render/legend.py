"""Legend helpers."""

from __future__ import annotations

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


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
    handles = [
        mpatches.Patch(color=colors.get(n, "#CCCCCC"), label=lbl)
        for n, lbl in zip(nodes, labels)
    ]
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

    fig_width_pt = fig.get_figwidth() * 72.0
    max_legend_pt = fig_width_pt * 1.25
    handle_pt = 30.0
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
