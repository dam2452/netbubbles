"""Example 8: Subgraph and edge filtering."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

g_full = nb.BubbleGraph.from_weighted_edges(
    {("A", "B"): 10, ("B", "C"): 7, ("C", "D"): 5,
     ("D", "A"): 3, ("A", "C"): 2, ("B", "D"): 8},
    colors={"A": "#E41A1C", "B": "#377EB8", "C": "#4DAF4A", "D": "#984EA3"},
)

g_sub = g_full.subgraph(["A", "B", "C"])
ax = nb.draw(g_sub, title="Subgraph", subtitle="Only A, B, C nodes")
ax.figure.savefig(f"{OUT}/8_subgraph.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/8_subgraph.png")

g_heavy = g_full.filter_edges(lambda e: e.weight >= 5)
ax2 = nb.draw(g_heavy, title="Filtered Edges", subtitle="Only weight >= 5")
ax2.figure.savefig(f"{OUT}/8b_filter.png", dpi=150, bbox_inches="tight")
plt.close(ax2.figure)
print(f"  {OUT}/8b_filter.png")
