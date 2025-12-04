import pytest

import janaf


def test_to_xarray():
    pytest.importorskip("xarray")
    pytest.importorskip("pint_xarray")

    t = janaf.search(formula="Fe", phase="ref")
    _ = t.to_xarray()
