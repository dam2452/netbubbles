"""Example 3: Bilayer layout - predator-prey food web."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

INNER = ["Wolf", "Eagle", "Lynx"]
OUTER = ["Rabbit", "Deer", "Mouse", "Salmon"]

PRED_COLORS = {"Wolf": "#2C3E50", "Eagle": "#8B4513", "Lynx": "#C0392B"}
PREY_COLORS = {
    "Rabbit": "#7FB3D3", "Deer": "#82E0AA",
    "Mouse":  "#F8C471", "Salmon": "#EC7063",
}

g = nb.BubbleGraph()
for n in INNER:
    g.add_node(n, color=PRED_COLORS[n], radius=0.20)
for n in OUTER:
    g.add_node(n, color=PREY_COLORS[n], radius=0.13)

g.add_edge("Wolf",  "Deer",   weight=7)
g.add_edge("Wolf",  "Rabbit", weight=5)
g.add_edge("Eagle", "Salmon", weight=6)
g.add_edge("Eagle", "Mouse",  weight=4)
g.add_edge("Lynx",  "Rabbit", weight=8)
g.add_edge("Lynx",  "Deer",   weight=3)
g.add_edge("Deer",  "Wolf",   weight=2)
g.add_edge("Rabbit","Lynx",   weight=2)

pos = nb.bilayer(INNER, OUTER)
style = nb.Style(
    background_circles=[
        (0, 0, 1.50 + 0.13 + 0.22, "#F5F5DC"),
        (0, 0, 0.60 + 0.20 + 0.12, "#E8F5E9"),
    ],
    arrowhead_length=0.115,
    arrowhead_width=0.07,
    title_fontsize=22,
)
all_colors = {**PRED_COLORS, **PREY_COLORS}
ax = nb.draw(
    g, pos=pos, title="Predator-Prey Food Web",
    subtitle="Inner ring: predators  |  Outer ring: prey",
    style=style, constrain_angles=False,
)
nb.add_legend(ax.figure, INNER + OUTER, all_colors)
ax.figure.savefig(f"{OUT}/3_bilayer.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/3_bilayer.svg")
