"""Example 4: Quick constructor — from_weighted_edges()."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

g = nb.BubbleGraph.from_weighted_edges(
    {
        ("Alpha", "Beta"):  10,
        ("Beta", "Gamma"):  7,
        ("Gamma", "Alpha"): 5,
        ("Alpha", "Gamma"): 3,
        ("Beta", "Alpha"):  2,
        ("Gamma", "Gamma"): 1,
    },
    colors={"Alpha": "#FF6B6B", "Beta": "#4ECDC4", "Gamma": "#45B7D1"},
)
ax = nb.draw(g, title="from_weighted_edges()", subtitle="Quick constructor")
ax.figure.savefig(f"{OUT}/4_weighted_edges.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/4_weighted_edges.png")
