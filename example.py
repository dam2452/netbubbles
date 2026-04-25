"""netbubbles demo — run this to generate example plots."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import netbubbles as nb
from netbubbles.presets import liana
from netbubbles.style import EdgeTier

OUT = Path(__file__).parent / "example_output"
OUT.mkdir(exist_ok=True)


# ── Kolory ───────────────────────────────────────────────────────
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

# ══════════════════════════════════════════════════════════════════
# 1. Prosty graf kolowy — circular layout
# ══════════════════════════════════════════════════════════════════
print("1. Circular network...")

g1 = nb.BubbleGraph()
for name, color in COLORS.items():
    g1.add_node(name, color=color)

g1.add_edge("T cell", "B cell", weight=8)
g1.add_edge("B cell", "T cell", weight=3)
g1.add_edge("T cell", "NK cell", weight=5)
g1.add_edge("Macrophage", "T cell", weight=7)
g1.add_edge("Macrophage", "Dendritic", weight=4)
g1.add_edge("Macrophage", "Macrophage", weight=2)
g1.add_edge("NK cell", "Fibroblast", weight=3)
g1.add_edge("Neutrophil", "Macrophage", weight=6)
g1.add_edge("Endothelial", "Fibroblast", weight=2)
g1.add_edge("Dendritic", "T cell", weight=5)
g1.add_edge("B cell", "Neutrophil", weight=1)

ax1 = nb.draw(g1, title="Cell Communication", subtitle="8 cell types, circular layout")
nb.add_legend(ax1.figure, sorted(COLORS.keys()), COLORS)
ax1.figure.savefig(OUT / "1_circular.png", dpi=150, bbox_inches="tight")
plt.close(ax1.figure)
print(f"   -> {OUT / '1_circular.png'}")


# ══════════════════════════════════════════════════════════════════
# 2. Focus — jeden node na srodku
# ══════════════════════════════════════════════════════════════════
print("2. Focus layout...")

g2 = nb.BubbleGraph()
g2.add_node("Macrophage", color="#911EB4", radius=0.46 * 1.6,
            label="MACs", label_position="center")
for n in ["T cell", "B cell", "NK cell", "Dendritic", "Fibroblast"]:
    g2.add_node(n, color=COLORS[n])

g2.add_edge("Macrophage", "T cell", weight=7)
g2.add_edge("Macrophage", "B cell", weight=5)
g2.add_edge("Macrophage", "NK cell", weight=3)
g2.add_edge("Macrophage", "Dendritic", weight=4)
g2.add_edge("Macrophage", "Fibroblast", weight=2)
g2.add_edge("NK cell", "Macrophage", weight=3)
g2.add_edge("T cell", "Macrophage", weight=4)

pos2 = nb.focus(g2.node_names, center="Macrophage")
ax2 = nb.draw(g2, pos=pos2, title="Focus: Macrophage", constrain_angles=False)
nb.add_legend(ax2.figure, g2.node_names, {n: COLORS.get(n, "#911EB4") for n in g2.node_names})
ax2.figure.savefig(OUT / "2_focus.png", dpi=150, bbox_inches="tight")
plt.close(ax2.figure)
print(f"   -> {OUT / '2_focus.png'}")


# ══════════════════════════════════════════════════════════════════
# 3. Bilayer — dwa piercienie (inner + outer)
# ══════════════════════════════════════════════════════════════════
print("3. Bilayer layout...")

INNER = ["Mac-1", "Mac-2", "Mac-3"]
OUTER = ["T cell", "B cell", "NK cell", "Fibroblast"]

MAC_COLORS = {"Mac-1": "#911EB4", "Mac-2": "#E41A1C", "Mac-3": "#FF7F00"}

g3 = nb.BubbleGraph()
for n in INNER:
    g3.add_node(n, color=MAC_COLORS[n], radius=0.20)
for n in OUTER:
    g3.add_node(n, color=COLORS[n], radius=0.13)

g3.add_edge("Mac-1", "T cell", weight=6)
g3.add_edge("Mac-2", "B cell", weight=4)
g3.add_edge("Mac-3", "NK cell", weight=3)
g3.add_edge("T cell", "Mac-1", weight=2)
g3.add_edge("NK cell", "Mac-3", weight=5)
g3.add_edge("Fibroblast", "Mac-2", weight=3)
g3.add_edge("Mac-1", "Mac-2", weight=2)

pos3 = nb.bilayer(INNER, OUTER)
style3 = nb.Style(
    background_circles=[
        (0, 0, 1.50 + 0.13 + 0.22, "#F0F4FA"),
        (0, 0, 0.60 + 0.20 + 0.12, "#E4EAF6"),
    ],
    arrowhead_length=0.115,
    arrowhead_width=0.07,
    title_fontsize=22,
)
all_colors = {**MAC_COLORS, **{n: COLORS[n] for n in OUTER}}
ax3 = nb.draw(g3, pos=pos3, title="Bilayer: Macrophage Subtypes",
              style=style3, constrain_angles=False)
nb.add_legend(ax3.figure, INNER + OUTER, all_colors)
ax3.figure.savefig(OUT / "3_bilayer.png", dpi=150, bbox_inches="tight")
plt.close(ax3.figure)
print(f"   -> {OUT / '3_bilayer.png'}")


# ══════════════════════════════════════════════════════════════════
# 4. from_weighted_edges — szybki konstruktor
# ══════════════════════════════════════════════════════════════════
print("4. from_weighted_edges...")

g4 = nb.BubbleGraph.from_weighted_edges(
    {
        ("Alpha", "Beta"):  10,
        ("Beta", "Gamma"):  7,
        ("Gamma", "Alpha"): 5,
        ("Alpha", "Gamma"): 3,
        ("Beta", "Alpha"):  2,
        ("Gamma", "Gamma"): 1,
    },
    colors={"Alpha": "#FF6B6B", "Beta": "#4ECDC4", "Gamma": "#45B7D1"},
)
ax4 = nb.draw(g4, title="from_weighted_edges()", subtitle="Quick constructor")
ax4.figure.savefig(OUT / "4_weighted_edges.png", dpi=150, bbox_inches="tight")
plt.close(ax4.figure)
print(f"   -> {OUT / '4_weighted_edges.png'}")


# ══════════════════════════════════════════════════════════════════
# 5. from_adjacency — z macierzy
# ══════════════════════════════════════════════════════════════════
print("5. from_adjacency...")

labels = ["A", "B", "C", "D"]
matrix = [
    [0, 8, 0, 3],
    [2, 0, 5, 0],
    [0, 0, 0, 7],
    [4, 0, 1, 0],
]
g5 = nb.BubbleGraph.from_adjacency(
    matrix, labels,
    colors={"A": "#FF6B6B", "B": "#4ECDC4", "C": "#45B7D1", "D": "#FFA07A"},
    threshold=0,
)
ax5 = nb.draw(g5, title="from_adjacency()", subtitle="4x4 matrix")
ax5.figure.savefig(OUT / "5_adjacency.png", dpi=150, bbox_inches="tight")
plt.close(ax5.figure)
print(f"   -> {OUT / '5_adjacency.png'}")


# ══════════════════════════════════════════════════════════════════
# 6. Custom Style — inn Kolory krawedzi, grubsze strzalki
# ══════════════════════════════════════════════════════════════════
print("6. Custom style...")

g6 = nb.BubbleGraph.from_weighted_edges(
    {("X", "Y"): 10, ("Y", "Z"): 7, ("Z", "X"): 5,
     ("X", "Z"): 3, ("Y", "X"): 8, ("Z", "Y"): 1},
    colors={"X": "#E41A1C", "Y": "#377EB8", "Z": "#4DAF4A"},
)
red_style = nb.Style(
    edge_tiers=[
        EdgeTier("#D62728", 4.5, 0.95),
        EdgeTier("#FF7F0E", 3.2, 0.80),
        EdgeTier("#2CA02C", 2.0, 0.60),
        EdgeTier("#AAAAAA", 1.2, 0.40),
    ],
    curve_strength=0.25,
    arrowhead_length=0.30,
    arrowhead_width=0.18,
    background_color="#FFF8F0",
)
ax6 = nb.draw(g6, title="Custom Style", subtitle="Red-orange edge tiers, wider arrows",
              style=red_style)
ax6.figure.savefig(OUT / "6_custom_style.png", dpi=150, bbox_inches="tight")
plt.close(ax6.figure)
print(f"   -> {OUT / '6_custom_style.png'}")


# ══════════════════════════════════════════════════════════════════
# 7. LIANA preset — symulowane dane
# ══════════════════════════════════════════════════════════════════
print("7. LIANA preset (simulated)...")

import pandas as pd
import numpy as np

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
df_liana = pd.DataFrame(rows)

g7 = liana.to_graph(df_liana, node_colors=COLORS)
ax7 = nb.draw(g7, title="LIANA Simulation", subtitle="200 random interactions")
nb.add_legend(ax7.figure, sorted(COLORS.keys()), COLORS)
ax7.figure.savefig(OUT / "7_liana.png", dpi=150, bbox_inches="tight")
plt.close(ax7.figure)
print(f"   -> {OUT / '7_liana.png'}")


# ══════════════════════════════════════════════════════════════════
# 8. Subgraph + filter_edges
# ══════════════════════════════════════════════════════════════════
print("8. Subgraph & filter...")

g8_full = nb.BubbleGraph.from_weighted_edges(
    {("A", "B"): 10, ("B", "C"): 7, ("C", "D"): 5,
     ("D", "A"): 3, ("A", "C"): 2, ("B", "D"): 8},
    colors={"A": "#E41A1C", "B": "#377EB8", "C": "#4DAF4A", "D": "#984EA3"},
)

g8_sub = g8_full.subgraph(["A", "B", "C"])
ax8 = nb.draw(g8_sub, title="Subgraph", subtitle="Only A, B, C nodes")
ax8.figure.savefig(OUT / "8_subgraph.png", dpi=150, bbox_inches="tight")
plt.close(ax8.figure)
print(f"   -> {OUT / '8_subgraph.png'}")

g8_heavy = g8_full.filter_edges(lambda e: e.weight >= 5)
ax8b = nb.draw(g8_heavy, title="Filtered Edges", subtitle="Only weight >= 5")
ax8b.figure.savefig(OUT / "8b_filter.png", dpi=150, bbox_inches="tight")
plt.close(ax8b.figure)
print(f"   -> {OUT / '8b_filter.png'}")


# ══════════════════════════════════════════════════════════════════
# 9. Multi-panel figure
# ══════════════════════════════════════════════════════════════════
print("9. Multi-panel figure...")

fig9, axes9 = plt.subplots(1, 3, figsize=(21, 7))
for ax in axes9:
    ax.set_aspect("equal")

graphs = [
    ("T1: Early", {("A","B"): 3, ("B","C"): 2, ("C","A"): 1}),
    ("T2: Mid",   {("A","B"): 7, ("B","C"): 5, ("C","A"): 4, ("A","C"): 2}),
    ("T3: Late",  {("A","B"): 10, ("B","C"): 8, ("C","A"): 6, ("A","C"): 5, ("B","A"): 3}),
]
colors_9 = {"A": "#E41A1C", "B": "#377EB8", "C": "#4DAF4A"}

for ax, (title, pairs) in zip(axes9, graphs):
    g = nb.BubbleGraph.from_weighted_edges(pairs, colors=colors_9)
    pos = nb.circular(g.node_names)
    nb.draw(g, ax=ax, pos=pos, title=title)

fig9.tight_layout()
fig9.savefig(OUT / "9_multipanel.png", dpi=150, bbox_inches="tight")
plt.close(fig9)
print(f"   -> {OUT / '9_multipanel.png'}")


# ══════════════════════════════════════════════════════════════════
# 10. LIANA merge_nodes — mergowanie subtypow
# ══════════════════════════════════════════════════════════════════
print("10. LIANA merge_nodes...")

g10 = nb.BubbleGraph()
for n, c in {**{"Mac-A1": "#911EB4", "Mac-A2": "#E41A1C"},
             **{n: COLORS[n] for n in ["T cell", "B cell", "NK cell"]}}.items():
    g10.add_node(n, color=c)
g10.add_edge("Mac-A1", "T cell", weight=5)
g10.add_edge("Mac-A2", "B cell", weight=3)
g10.add_edge("T cell", "Mac-A1", weight=2)

g10_merged = liana.merge_nodes(g10, "Mac", "Macrophage", merged_color="#911EB4")
# make center node bigger
g10_merged.nodes["Macrophage"].radius = 0.46 * 1.4
g10_merged.nodes["Macrophage"].label_position = "center"
g10_merged.nodes["Macrophage"].label = "MACs"

pos10 = nb.focus(g10_merged.node_names, center="Macrophage")
ax10 = nb.draw(g10_merged, pos=pos10, title="After merge_nodes()", subtitle="Mac-A1 + Mac-A2 → Macrophage", constrain_angles=False)
ax10.figure.savefig(OUT / "10_merge.png", dpi=150, bbox_inches="tight")
plt.close(ax10.figure)
print(f"   -> {OUT / '10_merge.png'}")


# ══════════════════════════════════════════════════════════════════
print()
print(f"Done! {len(list(OUT.glob('*.png')))} plots saved to {OUT}/")
print("Files:")
for f in sorted(OUT.glob("*.png")):
    print(f"  {f.name}")
