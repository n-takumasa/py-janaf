import pytest

import janaf


def test_db():
    assert janaf.db.shape == (1_796, 5)


def test_search_formula():
    t = janaf.search(formula="CO$")
    assert t.name == "Carbon Monoxide (CO)"
    assert t.formula == "C1O1(g)"


def test_search_name():
    t = janaf.search(name="Water, 1 Bar")
    assert t.name == "Water, 1 Bar (H2O)"
    assert t.formula == "H2O1(l,g)"


def test_search_phase():
    t = janaf.search(formula="Fe$", phase="ref")
    assert t.name == "Iron (Fe)"
    assert t.formula == "Fe1(ref)"


def test_notunique():
    with pytest.raises(janaf.index.NotUnique):
        _ = janaf.search(formula="Fe$")
