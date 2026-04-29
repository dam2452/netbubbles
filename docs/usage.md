# Usage

## Layouts

| Layout | Description | Use case |
|--------|-------------|----------|
| `circular` | Nodes on a circle | General networks, equal importance |
| `focus` | One node centered, rest on a ring | Hub-and-spoke, dominant node |
| `bilayer` | Two concentric rings | Compare inner vs outer groups |
| `grid` | Regular grid | Sequential or matrix layouts |
| `manual` | User-supplied coordinates | Full custom positioning |

```python
from netbubbles import circular, focus, bilayer, grid, manual

pos = circular(node_names, radius=3.0)
pos = focus(node_names, center="Hub")
pos = bilayer(inner_nodes, outer_nodes)
```

## Domain Presets

### LIANA - Cell-Cell Communication

```python
from netbubbles.presets import liana

df = liana.load_results(cache_dir)
g = liana.to_graph(df["timepoint_1"], node_colors=colors)
g_merged = liana.merge_nodes(g, "Mac", "Macrophage")
```

### Citation Networks

```python
from netbubbles.presets import citations

entries = citations.parse_bibtex("references.bib")
g = citations.to_graph(entries, citation_map=cites, mode="paper")
```

### Software Dependencies

```python
from netbubbles.presets import dependencies

deps = dependencies.parse_requirements("requirements.txt")
g = dependencies.to_graph(deps, root="my-app")
```

### Data Pipelines

```python
from netbubbles.presets import pipeline

steps = [
    {"name": "Extract", "type": "extract", "inputs": []},
    {"name": "Transform", "type": "transform", "inputs": ["Extract"]},
    {"name": "Load", "type": "store", "inputs": ["Transform"]},
]
g = pipeline.to_graph(steps)
```

### Web Link Graphs

```python
from netbubbles.presets import webgraph

links = {"home": ["about", "blog"], "blog": ["home", "post-1"]}
g = webgraph.from_links(links, root="home")
```

### Social Networks

```python
from netbubbles.presets import social

edges = [("Alice", "Bob", 12), ("Bob", "Alice", 10), ("Alice", "Carol", 5)]
g = social.from_edge_list(edges)
clusters = social.detect_clusters(g)
g_colored = social.from_edge_list(edges, clusters=clusters)
```

## Customization

### Style

```python
from netbubbles import Style
from netbubbles.style import EdgeTier

my_style = Style(
    node_edgecolor="black",
    node_edgewidth=2.0,
    shadow_offset=0.02,
    background_color="#F5F5F5",
    curve_strength=0.25,
    edge_tiers=[
        EdgeTier("#D62728", 4.5, 0.95),
        EdgeTier("#FF7F0E", 3.2, 0.80),
        EdgeTier("#2CA02C", 2.0, 0.60),
        EdgeTier("#AAAAAA", 1.2, 0.40),
    ],
    label_fontsize=14,
    title_fontsize=28,
)

ax = nb.draw(graph, style=my_style, title="Custom Styled")
```

### Graph Operations

```python
sub = g.subgraph(["A", "B", "C"])
heavy = g.filter_edges(lambda e: e.weight >= 5)
agg = g.aggregate_edges()
```

### Legends & Multi-Panel

```python
nb.add_legend(fig, node_names, color_dict)

fig, axes = plt.subplots(1, 3, figsize=(21, 7))
for ax, data in zip(axes, datasets):
    nb.draw(graph, ax=ax, title=data["label"])
```
