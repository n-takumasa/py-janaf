from __future__ import annotations

import io
import sys
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, Final

import polars as pl

from janaf._constant import UNITS_MAPPING

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

if TYPE_CHECKING:
    from collections.abc import Mapping

    import xarray as xr


@dataclass(frozen=True)
class Table:
    """Represents a NIST-JANAF Thermochemical Table."""

    index: str
    units: ClassVar[Final[Mapping[str, str]]] = UNITS_MAPPING

    @cached_property
    def fname(self) -> str:  # noqa: D102
        return f"data/{self.index}.txt"

    @cached_property
    def raw(self) -> str:  # noqa: D102
        return resources.files("janaf").joinpath(self.fname).read_text("utf-8")

    @cached_property
    def header(self) -> list[str]:  # noqa: D102
        return self.raw.split("\n", 1)[0].split("\t", 1)

    @cached_property
    def name(self) -> str:  # noqa: D102
        return self.header[0]

    @cached_property
    def formula(self) -> str:  # noqa: D102
        return self.header[1]

    @cached_property
    def body(self) -> str:  # noqa: D102
        return self.raw.split("\n", 1)[1]

    @cached_property
    def df(self) -> pl.DataFrame:
        """
        The table as a polars DataFrame.

        Columns
        -------
        - `T(K)`: Temperature [K]
        - `Cp`: Molar heat capacity at constant pressure [J/(K*mol)]
        - `S`: Molar entropy [J/(K*mol)]
        - `-[G-H(Tr)]/T`: Gibbs energy function [J/(K*mol)]
        - `H-H(Tr)`: Enthalpy increment [kJ/mol]
        - `delta-f H`: Enthalpy of formation
        - `delta-f G`: Gibbs energy of formation
        - `log Kf`: Logarithm (base 10) of equilibrium constant of formation
        - `Note`: Note string
        """
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

    def to_xarray(self) -> xr.Dataset:
        """
        Convert the Table to a xarray Dataset.

        Returns
        -------
        xarray.Dataset
            The temperature coordinate is renamed from `"T(K)"` to `"T"`

        Raises
        ------
        ModuleNotFoundError
        """
        try:
            import xarray as xr
        except ModuleNotFoundError as e:
            msg = "`xarray` is required for `to_xarray()`"
            raise ModuleNotFoundError(msg) from e

        ds = (
            xr.Dataset(
                {
                    col.name: (
                        (
                            ("index",),
                            col,
                            (
                                {"units": units}
                                if (units := self.units.get(col.name)) is not None
                                else {}
                            ),
                        )
                    )
                    for col in self.df.with_row_index().iter_columns()
                }
            )
            .set_coords("T(K)")
            .rename({"T(K)": "T"})
        )

        return ds
