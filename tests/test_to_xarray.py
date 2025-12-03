import janaf


def test_to_xarray():
    t = janaf.search(formula="Fe", phase="ref")
    _ = t.to_xarray()
