"""Example 14: Web link graph — page hyperlink network."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import webgraph

OUT = "example_output"

# Simulated website link structure
links = {
    "home":       ["about", "blog", "docs", "contact"],
    "about":      ["team", "careers"],
    "blog":       ["post-1", "post-2", "home"],
    "docs":       ["api", "tutorials", "home"],
    "contact":    ["home"],
    "team":       ["about"],
    "careers":    ["about", "home"],
    "post-1":     ["blog", "docs"],
    "post-2":     ["blog", "docs"],
    "api":        ["docs", "tutorials"],
    "tutorials":  ["docs", "api"],
}

g = webgraph.from_links(links, root="home")
ax = nb.draw(g, title="Web Link Graph", subtitle="11 pages, color by depth from home")
ax.figure.savefig(f"{OUT}/14_webgraph.png", dpi=150, bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/14_webgraph.png")
