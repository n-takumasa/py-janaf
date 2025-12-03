# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "janaf[xarray]",
#   "matplotlib",
# ]
# ///

import matplotlib.pyplot as plt
import pint
import pint_xarray  # type: ignore[import-untyped]

import janaf

# ureg = pint_xarray.unit_registry
ureg = pint_xarray.setup_registry(pint.UnitRegistry())
if pint.__version__ >= "v0.23.0":  # for py3.8
    ureg.formatter.default_format = "~P"

t = janaf.search(formula="Fe", phase="ref")
ds = t.to_xarray(ureg)

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
