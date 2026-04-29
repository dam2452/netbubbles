"""Example 5: Adjacency matrix constructor - flight hub connectivity."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

# Average daily connections between major hubs (thousands of seats)
labels = ["LHR", "JFK", "DXB", "SIN"]
matrix = [
    [0, 9, 7, 4],
    [8, 0, 5, 3],
    [6, 5, 0, 8],
    [3, 2, 9, 0],
]
g = nb.BubbleGraph.from_adjacency(
    matrix, labels,
    colors={
        "LHR": "#003087",
        "JFK": "#BF0A30",
        "DXB": "#009639",
        "SIN": "#EF3340",
    },
    threshold=0,
)
ax = nb.draw(g, title="Flight Hub Connectivity",
             subtitle="London · New York · Dubai · Singapore")
ax.figure.savefig(f"{OUT}/5_adjacency.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/5_adjacency.svg")
