"""Example 6: Custom Style - signal flow between brain regions."""

import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.style import EdgeTier

OUT = "example_output"

g = nb.BubbleGraph.from_weighted_edges(
    {
        ("Cortex",      "Hippocampus"): 10,
        ("Hippocampus", "Cortex"):       7,
        ("Cortex",      "Amygdala"):     8,
        ("Amygdala",    "Cortex"):       5,
        ("Hippocampus", "Amygdala"):     6,
        ("Amygdala",    "Hippocampus"):  3,
        ("Cortex",      "Cortex"):       2,
    },
    colors={
        "Cortex":      "#E41A1C",
        "Hippocampus": "#377EB8",
        "Amygdala":    "#4DAF4A",
    },
)
neuro_style = nb.Style(
    edge_tiers=[
        EdgeTier("#7B2D8B", 4.5, 0.95),
        EdgeTier("#C0392B", 3.2, 0.80),
        EdgeTier("#2471A3", 2.0, 0.60),
        EdgeTier("#AAAAAA", 1.2, 0.40),
    ],
    curve_strength=0.25,
    arrowhead_length=0.30,
    arrowhead_width=0.18,
    background_color="#F4F6F9",
    high_density="off",
)
ax = nb.draw(
    g, title="Brain Region Connectivity",
    subtitle="Signal flow with custom edge tiers", style=neuro_style,
)
ax.figure.savefig(f"{OUT}/6_custom_style.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/6_custom_style.svg")
