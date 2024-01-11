from __future__ import annotations

import polars as pl

from .index import search
from .table import Table

__version__ = "0.0.0"


def __getattr__(name):
    from .index import db

    if name == "db":
        return db()
    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)


db: pl.DataFrame
