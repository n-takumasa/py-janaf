import janaf
import pytest


@pytest.mark.parametrize("i", janaf.db["index"].tolist())
def test_runall(i):
    t = janaf.Table(i)
    assert (t.df[list(set(t.df.columns) - {"Note"})].dtypes == float).all()
