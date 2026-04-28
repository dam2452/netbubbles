"""Example 2: Focus layout — one node in the center."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

COLORS = {
    "T cell":     "#45B7D1",
    "B cell":     "#4ECDC4",
    "NK cell":    "#45B7D1",
    "Dendritic":  "#FFA07A",
    "Fibroblast": "#7FC97F",
}

g = nb.BubbleGraph()
g.add_node("Macrophage", color="#911EB4", radius=0.46 * 1.6,
           label="MACs", label_position="center")
for n in ["T cell", "B cell", "NK cell", "Dendritic", "Fibroblast"]:
    g.add_node(n, color=COLORS[n])

g.add_edge("Macrophage", "T cell", weight=7)
g.add_edge("Macrophage", "B cell", weight=5)
g.add_edge("Macrophage", "NK cell", weight=3)
g.add_edge("Macrophage", "Dendritic", weight=4)
g.add_edge("Macrophage", "Fibroblast", weight=2)
g.add_edge("NK cell", "Macrophage", weight=3)
g.add_edge("T cell", "Macrophage", weight=4)

pos = nb.focus(g.node_names, center="Macrophage")
ax = nb.draw(g, pos=pos, title="Focus: Macrophage", constrain_angles=False)
nb.add_legend(ax.figure, g.node_names, {n: COLORS.get(n, "#911EB4") for n in g.node_names})
ax.figure.savefig(f"{OUT}/2_focus.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/2_focus.png")
