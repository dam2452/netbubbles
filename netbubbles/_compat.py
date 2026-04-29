"""Compatibility shims for older Python versions."""

from __future__ import annotations

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self  # type: ignore[assignment]

__all__ = ["Self"]
