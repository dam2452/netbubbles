"""Example 7: LIANA preset - simulated cell-cell communication data."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import netbubbles as nb
from netbubbles.presets import liana

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

np.random.seed(42)
ligands = ["IL6", "TNF", "CXCL12", "TGFB1", "CCL2", "VEGFA"]
receptors = ["IL6R", "TNFRSF1A", "CXCR4", "TGFBR1", "CCR2", "VEGFR2"]
cells = list(COLORS.keys())

rows = []
for _ in range(200):
    rows.append({
        "source": np.random.choice(cells),
        "target": np.random.choice(cells),
        "ligand": np.random.choice(ligands),
        "receptor": np.random.choice(receptors),
        "rank_score": np.random.uniform(0.0, 0.3),
    })
df = pd.DataFrame(rows)

g = liana.to_graph(df, node_colors=COLORS)
ax = nb.draw(g, title="LIANA Simulation", subtitle="200 random interactions")
nb.add_legend(ax.figure, sorted(COLORS.keys()), COLORS)
ax.figure.savefig(f"{OUT}/7_liana.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/7_liana.svg")
