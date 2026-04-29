"""netbubbles.presets - domain-specific helpers for building graphs.

Each submodule provides parsers and ``to_graph()`` builders for a specific
data domain.  Import only what you need; submodules that depend on optional
packages (e.g. pandas) will raise an ImportError at use-time, not at
import-time.
"""

from . import (
    citations,
    dependencies,
    liana,
    pipeline,
    social,
    webgraph,
)
