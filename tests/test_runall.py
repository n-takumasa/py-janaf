import janaf
import pytest


@pytest.mark.parametrize("i", janaf.db["index"].tolist())
def test_runall(i):
    t = janaf.Table(i)
    df = t.df.reset_index()
    assert set(df.columns) == {
        "-[G-H(Tr)]/T",
        "Cp",
        "H-H(Tr)",
        "Note",
        "S",
        "T(K)",
        "delta-f G",
        "delta-f H",
        "log Kf",
    }
    assert (df[list(set(df.columns) - {"Note"})].dtypes == float).all()
