# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "janaf[xarray]",
#   "matplotlib",
#   "pint-xarray",
# ]
# ///

import matplotlib.pyplot as plt
import pint
import pint_xarray  # type: ignore[import-untyped]
import xarray as xr

import janaf

ureg = pint_xarray.setup_registry(pint.UnitRegistry())
ureg.formatter.default_format = "~P"

t = janaf.search(formula="Fe", phase="ref")
ds: xr.Dataset = t.to_xarray().pint.quantify(unit_registry=ureg)

fig, ax = plt.subplots()
ds["H-H(Tr)"].plot.line(".-", x="T", ax=ax)
plt.show()

fig, ax = plt.subplots()
(
    ds["H-H(Tr)"]
    .where(
        lambda x: (
            (x["T"] >= ureg.Quantity(0, "degC"))
            & (x["T"] <= ureg.Quantity(1800, "degC"))
        )
    )
    .pipe(lambda x: x / ureg("55.845 g/mol"))
    .pint.to("kWh/t")
    .plot.line(".-", x="T", ax=ax)
)
plt.show()
