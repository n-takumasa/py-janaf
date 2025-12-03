from __future__ import annotations

import io
import sys
from dataclasses import dataclass
from functools import cached_property

import polars as pl

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources


@dataclass(frozen=True)
class Table:
    index: str

    @cached_property
    def fname(self) -> str:
        return f"data/{self.index}.txt"

    @cached_property
    def raw(self) -> str:
        return resources.files("janaf").joinpath(self.fname).read_text("utf-8")

    @cached_property
    def header(self) -> list[str]:
        return self.raw.split("\n", 1)[0].split("\t", 1)

    @cached_property
    def name(self) -> str:
        return self.header[0]

    @cached_property
    def formula(self) -> str:
        return self.header[1]

    @cached_property
    def body(self) -> str:
        return self.raw.split("\n", 1)[1]

    @cached_property
    def df(self) -> pl.DataFrame:
        is_note = pl.col("delta-f H").str.contains(
            "<-->|TRANSITION|PRESSURE|FUGACITY|Cp|UNDEFINED"
        )
        return (
            pl.read_csv(
                io.StringIO(self.body),
                has_header=True,
                separator="\t",
                schema={
                    "T(K)": pl.Float64,
                    "Cp": pl.Float64,
                    "S": pl.Float64,
                    "-[G-H(Tr)]/T": pl.Float64,
                    "H-H(Tr)": pl.Float64,
                    "delta-f H": pl.String,
                    "delta-f G": pl.Float64,
                    "log Kf": pl.Float64,
                },
                truncate_ragged_lines=True,
            )
            .sort("T(K)")
            .with_columns(
                pl.when(is_note)
                .then(None)
                .otherwise(pl.col("delta-f H"))
                .cast(pl.Float64)
                .alias("delta-f H"),
                Note=pl.when(is_note).then(pl.col("delta-f H")),
            )
        )
