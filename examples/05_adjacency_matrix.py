"""Example 5: Adjacency matrix constructor — from_adjacency()."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

labels = ["A", "B", "C", "D"]
matrix = [
    [0, 8, 0, 3],
    [2, 0, 5, 0],
    [0, 0, 0, 7],
    [4, 0, 1, 0],
]
g = nb.BubbleGraph.from_adjacency(
    matrix, labels,
    colors={"A": "#FF6B6B", "B": "#4ECDC4", "C": "#45B7D1", "D": "#FFA07A"},
    threshold=0,
)
ax = nb.draw(g, title="from_adjacency()", subtitle="4x4 matrix")
ax.figure.savefig(f"{OUT}/5_adjacency.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/5_adjacency.png")
