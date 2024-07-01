from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import polars as pl

from janaf.table import Table


@lru_cache(maxsize=None)
def db() -> pl.DataFrame:
    return (
        pl.read_json(Path(__file__).parent / "janaf.json")
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
