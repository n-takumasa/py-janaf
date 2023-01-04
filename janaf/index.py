from functools import lru_cache
from pathlib import Path

import pandas as pd

from .table import Table


@lru_cache(maxsize=None)
def db() -> pd.DataFrame:
    org = pd.read_json(Path(__file__).parent / "janaf.json")
    df = org["display"].str.extract(
        r"^(?P<formula>[^,]+), (?P<name>.+) \((?P<phase>[^)]+)\)$"
    )
    return df.join(org)


class NotUnique(Exception):
    pass


def search(
    *,
    query: str | None = None,
    formula: str | None = None,
    name: str | None = None,
    phase: str | None = None,
):
    df = db().query(query) if query else db()
    result = pd.Series([True] * len(df), dtype=bool)

    if formula:
        result *= df["formula"].str.match(formula)
    if name:
        result *= df["name"].str.match(name)
    if phase:
        result *= df["phase"].str.match(phase)

    if result.sum() != 1:
        raise NotUnique("\n" + str(df[result]))
    return Table(index=df[result]["index"].iat[0])
