from __future__ import annotations

import json

import polars as pl
import pytest

import janaf


def get_index() -> list[str]:
    with open("src/janaf/janaf.json", "rb") as f:
        return json.load(f)["index"]


@pytest.mark.parametrize("index", get_index())
def test_columns(index: str):
    table = janaf.Table(index)
    assert table.df.columns == [
        "T(K)",
        "Cp",
        "S",
        "-[G-H(Tr)]/T",
        "H-H(Tr)",
        "delta-f H",
        "delta-f G",
        "log Kf",
        "Note",
    ]
    assert table.df.dtypes == [
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.String,
    ]
