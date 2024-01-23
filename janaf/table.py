from __future__ import annotations

import io
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import numpy as np
import polars as pl
import polars.selectors as cs


def _sign(x: str | float) -> int:  # pragma: no cover
    if isinstance(x, str):
        return -1 if x[0] == "-" else 1
    return np.sign(x)


def _fix_delta_f_H(df: pl.DataFrame) -> pl.DataFrame:
    df_fixed = (
        df.select(
            "index",
            pl.col("delta-f H", "delta-f G", "log Kf")
            .map_elements(_sign)
            .fill_null(strategy="backward")
            .shift(-1),
            #
            caps=pl.col("delta-f H").str.extract_groups(
                r"([-.\d]+)\s+([-.\d]+)\s+([-.\d]+)"
            ),
        )
        .unnest("caps")
        .select(
            "index",
            pl.col("delta-f H") * pl.col("1").cast(pl.Float64),
            pl.col("delta-f G") * pl.col("2").cast(pl.Float64),
            pl.col("log Kf") * pl.col("3").cast(pl.Float64),
        )
        .drop_nulls()
    )

    return df.update(df_fixed, on="index")


@dataclass(frozen=True)
class Table:
    index: str

    @cached_property
    def fname(self) -> Path:
        return Path(__file__).parent / f"data/{self.index}.txt"

    @cached_property
    def raw(self) -> str:
        with open(self.fname, encoding="utf-8") as f:
            return f.read()

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
        return "\n".join(
            line for line in self.raw.splitlines()[1:] if line[0] not in {"+", "H"}
        )

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
                dtypes={
                    "T(K)": pl.Float64,
                    "Cp": pl.Float64,
                    "S": pl.Float64,
                    "-[G-H(Tr)]/T": pl.String,
                    "H-H(Tr)": pl.Float64,
                    "delta-f H": pl.String,
                    "delta-f G": pl.Float64,
                    "log Kf": pl.String,
                },
                truncate_ragged_lines=True,
            )
            .sort("T(K)")
            .with_row_index(name="index")
            .with_columns(
                pl.when(is_note)
                .then(None)
                .otherwise(pl.col("delta-f H"))
                .alias("delta-f H"),
                Note=pl.when(is_note).then(pl.col("delta-f H")),
            )
            .pipe(_fix_delta_f_H)
            .with_columns(
                (cs.string() - cs.by_name("Note"))
                .str.replace_all("INFINITE", "+inf")
                .cast(pl.Float64)
            )
            .drop("index")
        )
