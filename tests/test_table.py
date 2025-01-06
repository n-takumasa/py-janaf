from __future__ import annotations

import json

import polars as pl
import pytest

import janaf


def get_index() -> list[str]:
    with open("src/janaf/janaf.json", "rb") as f:
        return json.load(f)["index"]


@pytest.mark.parametrize("index", get_index())
def test_table(index: str):
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

    # S(Tr) = -[G(Tr) - H(Tr)] / Tr
    if index not in {"S-016", "S-017", "S-018", "S-019", "S-020"}:
        assert (
            table.df.filter(pl.col("T(K)") == 298.15)
            .select(pl.col("S") - pl.col("-[G-H(Tr)]/T"))
            .item()
            == 0
        )

    # At constant pressure, enthalpy is a monotonically increasing function of temperature
    # TODO: https://github.com/n-takumasa/py-janaf/issues/13
    if index not in {"C-066", "Cl-121"}:
        assert table.df.select((pl.col("H-H(Tr)").diff() >= 0).all()).item()

    R = 8.31446261815324
    atol = 1e-3
    rtol = 1e-3
    # ΔG(T) = ΔfG°(T) + R T ln(Kf) = 0
    # ΔfG°(T) = - R T ln(Kf)
    # log10(Kf) = - ΔfG°(T) / (ln(10) * R * T)
    # TODO: https://github.com/n-takumasa/py-janaf/issues/13
    if index not in {"B-123", "B-133"}:
        assert (
            table.df.select(
                a="log Kf",
                b=(
                    (-1e3 * pl.col("delta-f G"))
                    / (pl.lit(10).log() * R * pl.col("T(K)"))
                ).fill_nan(0),
            )
            .with_columns(
                eq=(pl.col("a") == pl.col("b")),
                er_a=(pl.col("a") - pl.col("b")).abs(),
                er_r=(pl.col("a") - pl.col("b")).abs() / pl.col("b").abs(),
            )
            .with_columns(
                is_close=(pl.col("er_a") <= (atol + rtol * pl.col("b").abs())),
            )
            .select(
                q=(pl.col("eq") | pl.col("is_close")).all(),
            )
            .item()
        )

    # G-H-S relation
    # G°(T) = H°(T) - T S°(T)
    # S°(T) = [H°(T) - H°(Tr)]/T - [G°(T) - H°(Tr)]/T
    # TODO: https://github.com/n-takumasa/py-janaf/issues/13
    # fmt: off
    if index not in {
        "B-065", "B-116", "B-133", "Be-044", "Be-047", "C-002", "C-008", "C-010",
        "H-014", "H-016", "Hf-001", "Hf-002", "Hf-004", "Hf-005", "Li-014", "Li-016",
        "Mg-008", "Mg-010", "S-016", "S-017", "S-018", "S-019", "S-020",
    }:
        # fmt: on
        assert (
            table.df.select(
                "T(K)",
                a="S",
                b=(pl.col("H-H(Tr)") * 1e3 / pl.col("T(K)") + pl.col("-[G-H(Tr)]/T")),
            )
            .with_columns(
                eq=(pl.col("a") == pl.col("b")),
                er_a=(pl.col("a") - pl.col("b")).abs(),
                er_r=(pl.col("a") - pl.col("b")).abs() / pl.col("b").abs(),
            )
            .with_columns(
                is_close=(pl.col("er_a") <= (atol + rtol * pl.col("b").abs())),
            )
            .select(
                q=(pl.col("eq") | pl.col("is_close")).all(),
            )
            .item()
        )
