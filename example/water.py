# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "janaf",
#   "matplotlib",
# ]
# ///

import matplotlib.pyplot as plt
import polars as pl
from matplotlib.axes import Axes

import janaf

t = janaf.search(name="Water, 1 Bar")

fig, axes = plt.subplots(4, 2, sharex="col")
ax: Axes
for ax, col in zip(axes.flat, [c for c in t.df.columns if c not in {"T(K)", "Note"}]):
    ax.plot("T(K)", col, data=t.df)
    ax.set_title(col)
    if col in {"Cp", "S", "-[G-H(Tr)]/T"}:
        ax.set_ylabel(f"{col} J/K/mol")
    if col in {"H-H(Tr)", "delta-f H", "delta-f G"}:
        ax.set_ylabel(f"{col} kJ/mol")

xs = (
    t.df.drop_nulls("Note").select(pl.col("T(K)").unique()).get_column("T(K)").to_list()
)
for ax in axes.flat:
    for x in xs:
        ax.axvline(x, color="k", linestyle=":")

fig.suptitle(f"{t.name} {t.formula}")
fig.tight_layout()

plt.show()
