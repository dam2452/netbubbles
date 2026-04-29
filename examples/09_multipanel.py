"""Example 9: Multi-panel figure."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

fig, axes = plt.subplots(1, 3, figsize=(21, 7))
for ax in axes:
    ax.set_aspect("equal")

graphs = [
    ("T1: Early", {("A", "B"): 3, ("B", "C"): 2, ("C", "A"): 1}),
    ("T2: Mid",   {("A", "B"): 7, ("B", "C"): 5, ("C", "A"): 4, ("A", "C"): 2}),
    ("T3: Late",  {("A", "B"): 10, ("B", "C"): 8, ("C", "A"): 6, ("A", "C"): 5, ("B", "A"): 3}),
]
colors = {"A": "#E41A1C", "B": "#377EB8", "C": "#4DAF4A"}

for ax, (title, pairs) in zip(axes, graphs):
    g = nb.BubbleGraph.from_weighted_edges(pairs, colors=colors)
    pos = nb.circular(g.node_names)
    nb.draw(g, ax=ax, pos=pos, title=title)

fig.tight_layout()
fig.savefig(f"{OUT}/9_multipanel.svg", bbox_inches="tight")
plt.close(fig)
print(f"  {OUT}/9_multipanel.svg")
