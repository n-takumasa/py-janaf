import polars as pl
import pytest

import janaf


@pytest.mark.parametrize("i", janaf.db.get_column("index").to_list())
def test_runall(i):
    t = janaf.Table(i)
    assert t.df.columns == [
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
    assert t.df.dtypes == [
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
