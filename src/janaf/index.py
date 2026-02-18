from __future__ import annotations

from functools import cache
from importlib import resources

import polars as pl

from janaf.table import Table


@cache
def db() -> pl.DataFrame:  # noqa: D103
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


class NotUnique(Exception):  # noqa: D101, N818
    pass


def search(
    *,
    formula: str | None = None,
    name: str | None = None,
    phase: str | None = None,
) -> Table:
    """
    Search a compound.

    Parameters
    ----------
    formula
        Regex for `formula`, by default None.
    name
        Regex for `name`, by default None.
    phase
        Regex for `phase`, by default None.

    Returns
    -------
    janaf.Table
        The found table.

    Raises
    ------
    NotUnique
        Occurs when search results are not unique.
    """
    expr = pl.lit(value=True)
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
