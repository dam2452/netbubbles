"""netbubbles — directed bubble-graph visualisation with curved arrows.

A Python library for creating publication-quality bubble-graph
visualisations of directed weighted networks.
"""

from .graph import BubbleGraph, Edge, Node
from .layout import bilayer, circular, focus, grid, manual
from .render import add_legend, draw
from .style import Style, default_style

__all__ = [
    "BubbleGraph", "Node", "Edge",
    "draw", "add_legend",
    "circular", "bilayer", "focus", "grid", "manual",
    "Style", "default_style",
]
