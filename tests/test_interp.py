import janaf


def test_interp():
    t = janaf.search(formula="Fe", phase="ref")
    _ = t.interp(1873)
    _ = t.interp(1873, columns=["Cp", "H-H(Tr)"])
    _ = t.interp(1873, columns="H-H(Tr)")
    _ = t.interp([1823, 1873])
    _ = t.interp([1823, 1873], columns=["Cp", "H-H(Tr)"])
    _ = t.interp([1823, 1873], columns="H-H(Tr)")
