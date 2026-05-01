"""Example 2: Focus layout - central warehouse in a supply chain."""

import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

SUPPLIER_COLORS = {
    "Factory A":  "#E74C3C",
    "Factory B":  "#C0392B",
    "Retail":     "#2980B9",
    "E-commerce": "#1ABC9C",
    "Export":     "#8E44AD",
    "Returns":    "#F39C12",
}

g = nb.BubbleGraph()
g.add_node(
    "Warehouse", color="#2C3E50", radius=0.46 * 1.6,
    label="WH", label_position="center",
)
for n, c in SUPPLIER_COLORS.items():
    g.add_node(n, color=c)

g.add_edge("Factory A",  "Warehouse",  weight=9)
g.add_edge("Factory B",  "Warehouse",  weight=7)
g.add_edge("Warehouse",  "Retail",     weight=8)
g.add_edge("Warehouse",  "E-commerce", weight=10)
g.add_edge("Warehouse",  "Export",     weight=5)
g.add_edge("Returns",    "Warehouse",  weight=4)
g.add_edge("Warehouse",  "Factory A",  weight=3)
g.add_edge("E-commerce", "Returns",    weight=6)

pos = nb.focus(g.node_names, center="Warehouse")
ax = nb.draw(
    g, pos=pos, title="Supply Chain Hub",
    subtitle="Central warehouse: inbound vs outbound flows",
    constrain_angles=False,
    style=nb.Style(high_density="off"),
)
nb.add_legend(
    ax.figure, g.node_names,
    {n: SUPPLIER_COLORS.get(n, "#2C3E50") for n in g.node_names},
)
ax.figure.savefig(f"{OUT}/2_focus.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/2_focus.svg")
