"""Example 10: LIANA merge_nodes — merging subtypes."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import liana

OUT = "example_output"

COLORS = {"T cell": "#45B7D1", "B cell": "#4ECDC4", "NK cell": "#45B7D1"}

g = nb.BubbleGraph()
for n, c in {**{"Mac-A1": "#911EB4", "Mac-A2": "#E41A1C"},
             **{n: COLORS[n] for n in ["T cell", "B cell", "NK cell"]}}.items():
    g.add_node(n, color=c)
g.add_edge("Mac-A1", "T cell", weight=5)
g.add_edge("Mac-A2", "B cell", weight=3)
g.add_edge("T cell", "Mac-A1", weight=2)

g_merged = liana.merge_nodes(g, "Mac", "Macrophage", merged_color="#911EB4")
g_merged.nodes["Macrophage"].radius = 0.46 * 1.4
g_merged.nodes["Macrophage"].label_position = "center"
g_merged.nodes["Macrophage"].label = "MACs"

pos = nb.focus(g_merged.node_names, center="Macrophage")
ax = nb.draw(g_merged, pos=pos, title="After merge_nodes()",
             subtitle="Mac-A1 + Mac-A2 -> Macrophage", constrain_angles=False)
ax.figure.savefig(f"{OUT}/10_merge.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/10_merge.png")
