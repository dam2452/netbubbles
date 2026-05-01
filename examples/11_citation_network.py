"""Example 11: Citation network - bibliographic reference graph."""

import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import citations

OUT = "example_output"

# Simulated bibliography entries (as if parsed from a .bib file)
entries = [
    {"key": "smith2020", "title": "Deep Learning for Genomics", "author": "Smith, J", "year": "2020", "type": "article"},
    {"key": "jones2019", "title": "Neural Networks in Biology", "author": "Jones, A", "year": "2019", "type": "article"},
    {"key": "lee2021", "title": "Transformer Models for Proteins", "author": "Lee, S", "year": "2021", "type": "article"},
    {"key": "garcia2020", "title": "Single-Cell RNA-Seq Analysis", "author": "Garcia, M", "year": "2020", "type": "article"},
    {"key": "chen2018", "title": "Graph Neural Networks Survey", "author": "Chen, W", "year": "2018", "type": "article"},
    {"key": "park2022", "title": "Attention in Bioinformatics", "author": "Park, H", "year": "2022", "type": "article"},
    {"key": "brown2019", "title": "Transfer Learning Benchmarks", "author": "Brown, T", "year": "2019", "type": "inproceedings"},
    {"key": "wilson2021", "title": "Multi-Omics Integration", "author": "Wilson, R", "year": "2021", "type": "article"},
    {"key": "davis2020", "title": "Drug Discovery with ML", "author": "Davis, K", "year": "2020", "type": "article"},
    {"key": "taylor2022", "title": "Foundation Models in Science", "author": "Taylor, B", "year": "2022", "type": "article"},
]

# Citation map: paper -> [papers it cites]
citation_map = {
    "smith2020": ["jones2019", "chen2018", "brown2019"],
    "lee2021": ["smith2020", "jones2019", "chen2018"],
    "garcia2020": ["jones2019", "davis2020"],
    "park2022": ["lee2021", "smith2020", "brown2019"],
    "wilson2021": ["smith2020", "garcia2020"],
    "davis2020": ["chen2018", "brown2019"],
    "taylor2022": ["lee2021", "park2022", "wilson2021"],
}

g = citations.to_graph(entries, citation_map=citation_map, mode="paper")
ax = nb.draw(g, title="Citation Network", subtitle="10 papers, color by year", style=nb.Style(high_density="off"))
ax.figure.savefig(f"{OUT}/11_citation_network.svg", bbox_inches="tight")
plt.close(ax.figure)
print(f"  {OUT}/11_citation_network.svg")

# Author-level aggregation
_PALETTE = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#A65628", "#F781BF", "#999999"]
g_author = citations.to_graph(entries, citation_map=citation_map, mode="author")
author_colors = {a: _PALETTE[i % len(_PALETTE)] for i, a in enumerate(sorted(g_author.nodes.keys()))}
ax2 = nb.draw(g_author, title="Author Citation Network", subtitle="Aggregated by first author", style=nb.Style(high_density="off"))
ax2.figure.savefig(f"{OUT}/11b_author_citations.svg", bbox_inches="tight")
plt.close(ax2.figure)
print(f"  {OUT}/11b_author_citations.svg")
