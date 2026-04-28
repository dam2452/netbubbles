"""Example 3: Bilayer layout — two concentric rings."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

INNER = ["Mac-1", "Mac-2", "Mac-3"]
OUTER = ["T cell", "B cell", "NK cell", "Fibroblast"]

MAC_COLORS = {"Mac-1": "#911EB4", "Mac-2": "#E41A1C", "Mac-3": "#FF7F00"}
COLORS = {"T cell": "#45B7D1", "B cell": "#4ECDC4", "NK cell": "#45B7D1", "Fibroblast": "#7FC97F"}

g = nb.BubbleGraph()
for n in INNER:
    g.add_node(n, color=MAC_COLORS[n], radius=0.20)
for n in OUTER:
    g.add_node(n, color=COLORS[n], radius=0.13)

g.add_edge("Mac-1", "T cell", weight=6)
g.add_edge("Mac-2", "B cell", weight=4)
g.add_edge("Mac-3", "NK cell", weight=3)
g.add_edge("T cell", "Mac-1", weight=2)
g.add_edge("NK cell", "Mac-3", weight=5)
g.add_edge("Fibroblast", "Mac-2", weight=3)
g.add_edge("Mac-1", "Mac-2", weight=2)

pos = nb.bilayer(INNER, OUTER)
style = nb.Style(
    background_circles=[
        (0, 0, 1.50 + 0.13 + 0.22, "#F0F4FA"),
        (0, 0, 0.60 + 0.20 + 0.12, "#E4EAF6"),
    ],
    arrowhead_length=0.115,
    arrowhead_width=0.07,
    title_fontsize=22,
)
all_colors = {**MAC_COLORS, **{n: COLORS[n] for n in OUTER}}
ax = nb.draw(g, pos=pos, title="Bilayer: Macrophage Subtypes",
             style=style, constrain_angles=False)
nb.add_legend(ax.figure, INNER + OUTER, all_colors)
ax.figure.savefig(f"{OUT}/3_bilayer.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/3_bilayer.png")
