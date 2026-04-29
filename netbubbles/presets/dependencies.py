"""Software dependency graph helpers."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
from typing import (
    Dict,
    List,
    Optional,
)

from ..graph import BubbleGraph
from ._common import (
    compute_depths,
    palette_color,
)

# pylint: disable=missing-param-doc




def _layer_color(depth: int) -> str:
    return palette_color(min(depth, 6))


# ── Parsers ──────────────────────────────────────────────────────

def parse_requirements(path: str | Path) -> Dict[str, List[str]]:
    """Parse a requirements.txt into ``{package: [deps]}``.

    For requirements.txt this is flat - each package has no sub-deps
    listed, so each maps to an empty list.
    """
    deps: Dict[str, List[str]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[><=!~\[]", line)[0].strip().lower()
        if name:
            deps[name] = []
    return deps


def parse_package_json(path: str | Path) -> Dict[str, List[str]]:
    """Parse package.json dependencies into ``{package: [deps]}``.

    Returns both ``dependencies`` and ``devDependencies``.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    deps: Dict[str, List[str]] = {}
    for section in ("dependencies", "devDependencies"):
        for name in data.get(section, {}):
            deps[name] = []
    return deps


def parse_python_imports(path: str | Path) -> Dict[str, List[str]]:
    """Analyze a single Python file and return ``{module: [imports]}``."""
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    module_name = Path(path).stem
    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return {module_name: list(set(imports))}


# ── Graph builder ────────────────────────────────────────────────

def to_graph(
    deps: Dict[str, List[str]],
    *,
    root: Optional[str] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Convert a dependency tree to a BubbleGraph.

    Parameters
    ----------
    deps:
        ``{package: [its_dependencies]}`` mapping.
    root:
        Optional root package name. If given, it is drawn larger.
    """
    g = BubbleGraph()

    all_names = set(deps.keys())
    for sub_deps in deps.values():
        all_names.update(sub_deps)

    depths = compute_depths(deps, root)

    for name in sorted(all_names):
        d = depths.get(name, 99)
        color = (node_colors or {}).get(name, _layer_color(d))
        r = node_radius * 1.3 if name == root else node_radius
        g.add_node(
            name, color=color, radius=r, label=name,
            label_position="center" if name == root else "outer",
        )

    for pkg, sub_deps in deps.items():
        for dep in sub_deps:
            g.add_edge(pkg, dep, weight=1.0)

    return g
