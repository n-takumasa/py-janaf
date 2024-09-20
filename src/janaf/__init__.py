from __future__ import annotations

from typing import TYPE_CHECKING

from janaf import index, table
from janaf._version import __version__
from janaf.index import search
from janaf.table import Table

if TYPE_CHECKING:
    from typing import Any

    import polars as pl


def __getattr__(name: str) -> Any:
    from janaf.index import db

    if name == "db":
        return db()
    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)


db: pl.DataFrame

__all__ = [
    "__version__",
    "db",
    "index",
    "search",
    "table",
    "Table",
]
