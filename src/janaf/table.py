from __future__ import annotations

import io
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, Final

import polars as pl

from janaf._constant import UNITS_MAPPING

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources

if TYPE_CHECKING:
    import pint
    import xarray as xr


@dataclass(frozen=True)
class Table:
    index: str
    units: ClassVar[Final[Mapping[str, str]]] = UNITS_MAPPING

    @cached_property
    def fname(self) -> str:
        return f"data/{self.index}.txt"

    @cached_property
    def raw(self) -> str:
        return resources.files("janaf").joinpath(self.fname).read_text("utf-8")

    @cached_property
    def header(self) -> list[str]:
        return self.raw.split("\n", 1)[0].split("\t", 1)

    @cached_property
    def name(self) -> str:
        return self.header[0]

    @cached_property
    def formula(self) -> str:
        return self.header[1]

    @cached_property
    def body(self) -> str:
        return self.raw.split("\n", 1)[1]

    @cached_property
    def df(self) -> pl.DataFrame:
        is_note = pl.col("delta-f H").str.contains(
            "<-->|TRANSITION|PRESSURE|FUGACITY|Cp|UNDEFINED"
        )
        return (
            pl.read_csv(
                io.StringIO(self.body),
                has_header=True,
                separator="\t",
                schema={
                    "T(K)": pl.Float64,
                    "Cp": pl.Float64,
                    "S": pl.Float64,
                    "-[G-H(Tr)]/T": pl.Float64,
                    "H-H(Tr)": pl.Float64,
                    "delta-f H": pl.String,
                    "delta-f G": pl.Float64,
                    "log Kf": pl.Float64,
                },
                truncate_ragged_lines=True,
            )
            .sort("T(K)")
            .with_columns(
                pl.when(is_note)
                .then(None)
                .otherwise(pl.col("delta-f H"))
                .cast(pl.Float64)
                .alias("delta-f H"),
                Note=pl.when(is_note).then(pl.col("delta-f H")),
            )
        )

    def to_xarray(
        self,
        unit_registry: pint.UnitRegistry[Any] | None = None,
    ) -> xr.Dataset:
        """
        Convert this Table to a xarray Dataset.

        Parameters
        ----------
        unit_registry, optional
            Argument for `Dataset.pint.quantify`

        Returns
        -------
        xarray.Dataset
            The temperature coordinate is renamed from `"T(K)"` to `"T"`
        """
        try:
            import xarray as xr
        except ImportError as e:
            msg = "`xarray` is required for `to_xarray()`"
            raise ImportError(msg) from e

        ds = (
            self.df.to_pandas(use_pyarrow_extension_array=False)
            .pipe(xr.Dataset.from_dataframe)
            .set_coords("T(K)")
        )

        try:
            import pint_xarray  # type: ignore[import-untyped] # noqa: F401

            ds = ds.pint.quantify(self.units, unit_registry)
        except ImportError:
            pass

        ds = ds.rename({"T(K)": "T"})
        return ds
