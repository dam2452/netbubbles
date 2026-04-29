"""Example 13: Data pipeline / ETL flow graph."""

import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import pipeline

OUT = "example_output"

steps = [
    {"name": "Raw Data",    "type": "extract",   "inputs": []},
    {"name": "Clean",       "type": "transform", "inputs": ["Raw Data"]},
    {"name": "Validate",    "type": "validate",  "inputs": ["Clean"]},
    {"name": "Feature Eng", "type": "transform", "inputs": ["Validate"]},
    {"name": "Aggregate",   "type": "aggregate", "inputs": ["Feature Eng"]},
    {"name": "DB Write",    "type": "store",     "inputs": ["Aggregate"]},
    {"name": "API Export",  "type": "output",    "inputs": ["Aggregate"]},
    {"name": "Dashboard",   "type": "output",    "inputs": ["DB Write"]},
]

g = pipeline.to_graph(steps)
ax = nb.draw(g, title="Data Pipeline", subtitle="ETL flow: extract -> transform -> load")
ax.figure.savefig(f"{OUT}/13_pipeline.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/13_pipeline.svg")
