import pandas as pd

from .index import search
from .table import Table

__version__ = "0.0.0"


def __getattr__(name):
    from .index import db

    if name == "db":
        return db()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


db: pd.DataFrame
