"""Example 1: Basic circular network."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

COLORS = {
    "T cell":      "#FF6B6B",
    "B cell":      "#4ECDC4",
    "NK cell":     "#45B7D1",
    "Macrophage":  "#911EB4",
    "Dendritic":   "#FFA07A",
    "Fibroblast":  "#7FC97F",
    "Neutrophil":  "#FDC086",
    "Endothelial": "#BEAED4",
}

g = nb.BubbleGraph()
for name, color in COLORS.items():
    g.add_node(name, color=color)

g.add_edge("T cell", "B cell", weight=8)
g.add_edge("B cell", "T cell", weight=3)
g.add_edge("T cell", "NK cell", weight=5)
g.add_edge("Macrophage", "T cell", weight=7)
g.add_edge("Macrophage", "Dendritic", weight=4)
g.add_edge("Macrophage", "Macrophage", weight=2)
g.add_edge("NK cell", "Fibroblast", weight=3)
g.add_edge("Neutrophil", "Macrophage", weight=6)
g.add_edge("Endothelial", "Fibroblast", weight=2)
g.add_edge("Dendritic", "T cell", weight=5)
g.add_edge("B cell", "Neutrophil", weight=1)

ax = nb.draw(g, title="Cell Communication", subtitle="8 cell types, circular layout")
nb.add_legend(ax.figure, sorted(COLORS.keys()), COLORS)
ax.figure.savefig(f"{OUT}/1_circular.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/1_circular.svg")
