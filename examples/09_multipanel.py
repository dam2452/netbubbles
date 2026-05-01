"""Example 9: Multi-panel figure - media consumption shift over decades."""

import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

COLORS = {
    "Broadcast": "#E41A1C",
    "Print":     "#377EB8",
    "Digital":   "#4DAF4A",
}

panels = [
    (
        "2000s: Broadcast Era",
        {
            ("Broadcast", "Print"):   6,
            ("Print",     "Broadcast"): 4,
            ("Broadcast", "Digital"): 2,
            ("Digital",   "Broadcast"): 1,
            ("Print",     "Digital"): 3,
        },
    ),
    (
        "2010s: Convergence",
        {
            ("Broadcast", "Digital"): 7,
            ("Digital",   "Broadcast"): 5,
            ("Print",     "Digital"): 8,
            ("Digital",   "Print"):   4,
            ("Broadcast", "Print"):   3,
        },
    ),
    (
        "2020s: Digital-First",
        {
            ("Digital",   "Broadcast"): 9,
            ("Digital",   "Print"):     8,
            ("Broadcast", "Digital"):   5,
            ("Print",     "Digital"):   4,
            ("Broadcast", "Print"):     2,
            ("Digital",   "Digital"):   3,
        },
    ),
]

fig, axes = plt.subplots(1, 3, figsize=(21, 7))

for ax, (title, pairs) in zip(axes, panels):
    g = nb.BubbleGraph.from_weighted_edges(pairs, colors=COLORS)
    pos = nb.circular(g.node_names)
    nb.draw(g, ax=ax, pos=pos, title=title, style=nb.Style(high_density="off"))

fig.tight_layout()
fig.savefig(f"{OUT}/9_multipanel.svg", bbox_inches="tight")
plt.close(fig)
print(f"  {OUT}/9_multipanel.svg")
