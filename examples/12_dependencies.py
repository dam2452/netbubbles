"""Example 12: Software dependency graph."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import dependencies

OUT = "example_output"

# Simulated Flask-like dependency tree
deps = {
    "flask":       ["werkzeug", "jinja2", "click", "itsdangerous"],
    "werkzeug":    ["markupsafe"],
    "jinja2":      ["markupsafe"],
    "click":       [],
    "itsdangerous": [],
    "markupsafe":  [],
}

g = dependencies.to_graph(deps, root="flask")
ax = nb.draw(g, title="Software Dependencies", subtitle="Flask dependency tree")
ax.figure.savefig(f"{OUT}/12_dependencies.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/12_dependencies.png")
