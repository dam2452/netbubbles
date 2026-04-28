"""Example 6: Custom Style — different edge colors and thicker arrows."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.style import EdgeTier

OUT = "example_output"

g = nb.BubbleGraph.from_weighted_edges(
    {("X", "Y"): 10, ("Y", "Z"): 7, ("Z", "X"): 5,
     ("X", "Z"): 3, ("Y", "X"): 8, ("Z", "Y"): 1},
    colors={"X": "#E41A1C", "Y": "#377EB8", "Z": "#4DAF4A"},
)
red_style = nb.Style(
    edge_tiers=[
        EdgeTier("#D62728", 4.5, 0.95),
        EdgeTier("#FF7F0E", 3.2, 0.80),
        EdgeTier("#2CA02C", 2.0, 0.60),
        EdgeTier("#AAAAAA", 1.2, 0.40),
    ],
    curve_strength=0.25,
    arrowhead_length=0.30,
    arrowhead_width=0.18,
    background_color="#FFF8F0",
)
ax = nb.draw(g, title="Custom Style", subtitle="Red-orange edge tiers, wider arrows",
             style=red_style)
ax.figure.savefig(f"{OUT}/6_custom_style.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/6_custom_style.png")
