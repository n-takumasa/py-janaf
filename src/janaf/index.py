from __future__ import annotations

import sys
from functools import lru_cache

import polars as pl

from janaf.table import Table

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources


@lru_cache(maxsize=None)
def db() -> pl.DataFrame:
    src = resources.files("janaf").joinpath("janaf.json").read_bytes()
    return (
        pl.read_json(src)
        .explode("*")
        .with_columns(
            pl.col("display")
            .str.extract_groups(
                r"^(?P<formula>[^,]+), (?P<name>.+) \((?P<phase>[^)]+)\)$"
            )
            .alias("_")
        )
        .unnest("_")
    )


class NotUnique(Exception):  # noqa: N818
    pass


def search(
    *,
    formula: str | None = None,
    name: str | None = None,
    phase: str | None = None,
) -> Table:
    """Search a compound

    Parameters
    ----------
    formula, optional
        Regex for `formula`, by default None
    name, optional
        Regex for `name`, by default None
    phase, optional
        Regex for `phase`, by default None

    Returns
    -------
        `janaf.Table`

    Raises
    ------
    NotUnique
        Occurs when search results are not unique
    """

    expr = pl.lit(True)
    if formula:
        expr &= pl.col("formula").str.contains(
            formula if formula[0] == "^" else f"^{formula}"
        )
    if name:
        expr &= pl.col("name").str.contains(name if name[0] == "^" else f"^{name}")
    if phase:
        expr &= pl.col("phase").str.contains(phase if phase[0] == "^" else f"^{phase}")
    result = db().filter(expr)

    if len(result) != 1:
        raise NotUnique("\n" + str(result))
    return Table(index=result.select("index").item())
