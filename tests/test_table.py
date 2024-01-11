import polars as pl
import pytest

import janaf


@pytest.fixture()
def table(request: pytest.FixtureRequest):
    return janaf.Table(request.param)


db_indexes = janaf.db.get_column("index").to_list()


@pytest.mark.parametrize("index", db_indexes)
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


# def test_monotonic(table: janaf.Table):
#     ...
