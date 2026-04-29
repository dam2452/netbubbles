"""Example 4: Quick constructor - global trade flows between economic blocs."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

g = nb.BubbleGraph.from_weighted_edges(
    {
        ("Americas", "Europe"):   8,
        ("Europe",   "Americas"): 6,
        ("Europe",   "Asia"):     9,
        ("Asia",     "Europe"):   7,
        ("Asia",     "Americas"): 10,
        ("Americas", "Asia"):     5,
        ("Asia",     "Asia"):     3,
    },
    colors={
        "Americas": "#E41A1C",
        "Europe":   "#377EB8",
        "Asia":     "#4DAF4A",
    },
)
ax = nb.draw(
    g, title="Global Trade Flows",
    subtitle="Inter-regional merchandise trade volumes",
)
ax.figure.savefig(f"{OUT}/4_weighted_edges.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/4_weighted_edges.svg")
