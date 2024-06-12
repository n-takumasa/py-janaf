from __future__ import annotations

from typing import TYPE_CHECKING

from janaf.index import search
from janaf.table import Table

if TYPE_CHECKING:
    import polars as pl

__version__ = "0.0.0"


def __getattr__(name):
    from janaf.index import db

    if name == "db":
        return db()
    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)


db: pl.DataFrame
