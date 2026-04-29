"""Example 8: Subgraph and edge filtering - DevOps pipeline stages."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb

OUT = "example_output"

g_full = nb.BubbleGraph.from_weighted_edges(
    {
        ("Plan",    "Code"):    6,
        ("Code",    "Build"):   9,
        ("Build",   "Test"):    8,
        ("Test",    "Deploy"):  5,
        ("Deploy",  "Monitor"): 7,
        ("Monitor", "Plan"):    4,
        ("Test",    "Code"):    6,
    },
    colors={
        "Plan":    "#8E44AD",
        "Code":    "#2980B9",
        "Build":   "#27AE60",
        "Test":    "#F39C12",
        "Deploy":  "#E74C3C",
        "Monitor": "#16A085",
    },
)

g_sub = g_full.subgraph(["Plan", "Code", "Build", "Test"])
ax = nb.draw(g_sub, title="Dev Stages", subtitle="Plan → Code → Build → Test")
ax.figure.savefig(f"{OUT}/8_subgraph.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/8_subgraph.svg")

g_critical = g_full.filter_edges(lambda e: e.weight >= 7)
ax2 = nb.draw(g_critical, title="Critical Flows",
              subtitle="High-throughput pipeline paths (weight ≥ 7)")
ax2.figure.savefig(f"{OUT}/8b_filter.svg", bbox_inches="tight")
plt.close(ax2.figure)
print(f"  {OUT}/8b_filter.svg")
