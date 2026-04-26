"""Style configuration for node and edge rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class EdgeTier:
    color: str
    linewidth: float
    alpha: float


@dataclass
class Style:
    # ── Node ─────────────────────────────────────────────────────
    node_edgecolor: str = "white"
    node_edgewidth: float = 2.8
    shadow_offset: float = 0.018
    shadow_color: str = "#00000022"
    highlight: bool = True
    highlight_offset: Tuple[float, float] = (0.28, 0.28)
    highlight_radius_frac: float = 0.42
    highlight_alpha: float = 0.22

    # ── Edge ─────────────────────────────────────────────────────
    max_edges: int = 100
    edge_tiers: List[EdgeTier] = field(default_factory=lambda: [
        EdgeTier("#7B2D8B", 3.6, 0.88),
        EdgeTier("#1A6FA8", 2.56, 0.74),
        EdgeTier("#49A62D", 1.68, 0.60),
        EdgeTier("#999999", 0.96, 0.45),
    ])

    # ── Arrow geometry ───────────────────────────────────────────
    curve_strength: float = 0.18
    arrowhead_length: float = 0.23
    arrowhead_width: float = 0.14
    arrow_spread_rad: float = float(np.radians(15.0))

    # ── Self-loop ────────────────────────────────────────────────
    self_loop_radius_frac: float = 0.6
    self_loop_gap_deg: float = 30.0

    # ── Layout & background ──────────────────────────────────────
    axis_margin: float = 1.1
    background_color: str = "#F0F4FA"
    background_circles: Optional[List[Tuple[float, float, float, str]]] = None
    ax_facecolor: Optional[str] = None

    # ── Text ─────────────────────────────────────────────────────
    label_fontsize: float = 12.0
    center_label_fontsize: float = 12.0
    label_offset: float = 0.08
    label_color: str = "black"
    center_label_color: str = "black"
    label_stroke_color: Optional[str] = None
    label_stroke_width: float = 2.5
    title_fontsize: float = 25.0
    title_pad: float = 26.0
    subtitle_fontsize_ratio: float = 0.5
    subtitle_pad: float = 2.0

    # ── Methods ──────────────────────────────────────────────────

    def tier_for(self, frac: float) -> EdgeTier:
        idx = min(len(self.edge_tiers) - 1, int((1.0 - frac) * len(self.edge_tiers)))
        return self.edge_tiers[idx]

    def edge_color(self, frac: float) -> str:
        return self.tier_for(frac).color

    def edge_linewidth(self, frac: float) -> float:
        return self.tier_for(frac).linewidth

    def edge_alpha(self, frac: float) -> float:
        return self.tier_for(frac).alpha


default_style = Style()
