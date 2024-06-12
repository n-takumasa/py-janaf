# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "janaf",
#   "matplotlib",
# ]
# ///

import matplotlib.pyplot as plt
import polars as pl

import janaf

t = janaf.search(name="Water, 1 Bar")

df = t.df.to_pandas(use_pyarrow_extension_array=True).set_index("T(K)")  # noqa: PD901

fig, axes = plt.subplots(4, 2, sharex="col")
for ax, col in zip(axes.flat, [c for c in df.columns if c not in {"Note"}]):
    ax: plt.Axes
    df.plot(y=col, ax=ax, legend=False)
    ax.set_title(col)
    if col in {"Cp", "S", "-[G-H(Tr)]/T"}:
        ax.set_ylabel(f"{col} J/K/mol")
    if col in {"H-H(Tr)", "delta-f H", "delta-f G"}:
        ax.set_ylabel(f"{col} kJ/mol")

xs = (
    t.df.drop_nulls("Note").select(pl.col("T(K)").unique()).get_column("T(K)").to_list()
)
for ax in axes.flat:
    ax: plt.Axes
    for x in xs:
        ax.axvline(x, color="k", linestyle=":")

fig.suptitle(f"{t.name} {t.formula}")
fig.tight_layout()
plt.show()
