# Examples

All runnable scripts are in the [`examples/`](../examples/) directory. Generate every output at once:

```bash
cd examples && python generate_all.py
```

## Index

| # | File | Description |
|---|------|-------------|
| 01 | `01_basic_network.py` | Circular layout with 8 nodes - the simplest starting point |
| 02 | `02_focus_layout.py` | Hub-and-spoke: one dominant center node, rest on a ring |
| 03 | `03_bilayer_layout.py` | Bilayer: inner and outer concentric rings |
| 04 | `04_weighted_edges.py` | `BubbleGraph.from_weighted_edges()` shorthand constructor |
| 05 | `05_adjacency_matrix.py` | Build a graph from an adjacency matrix |
| 06 | `06_custom_style.py` | Custom `Style` object with edge tiers and colour overrides |
| 07 | `07_liana_preset.py` | LIANA cell-cell communication preset |
| 08 | `08_subgraph_filter.py` | Subgraph extraction and edge weight filtering |
| 09 | `09_multipanel.py` | Multi-panel time series in a single figure |
| 10 | `10_merge_nodes.py` | Merging nodes by group label |
| 11 | `11_citation_network.py` | Bibliographic citation network from BibTeX |
| 12 | `12_dependencies.py` | Software dependency tree from `requirements.txt` |
| 13 | `13_pipeline.py` | Data pipeline / ETL flow |
| 14 | `14_webgraph.py` | Web page link graph |
| 15 | `15_social_network.py` | Social network with community detection |

## Previews

### Layouts

| Circular (`01`) | Focus (`02`) | Bilayer (`03`) |
|---|---|---|
| ![circular](../example_output/1_circular.svg) | ![focus](../example_output/2_focus.svg) | ![bilayer](../example_output/3_bilayer.svg) |

### Presets & Advanced

| Citation (`11`) | Social (`15`) | Multi-panel (`09`) |
|---|---|---|
| ![citation](../example_output/11_citation_network.svg) | ![social](../example_output/15_social_network.svg) | ![multipanel](../example_output/9_multipanel.svg) |
