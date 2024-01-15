# py-janaf: Python wrapper for NIST-JANAF Thermochemical Tables
[![pypi version](https://img.shields.io/pypi/v/janaf.svg)](https://pypi.python.org/project/janaf/)
[![Python Versions](https://img.shields.io/pypi/pyversions/janaf.svg)](https://pypi.org/project/janaf/)

## Features

* Search compounds
* Parse a table as `polars.DataFrame`
* Fix some data
  * [Fix missing sign](https://github.com/n-takumasa/py-janaf/commit/7f56ce84bb65c90dd4ecd2efdca2d6f8fe1243b5)
    * NOTE: Assuming the sign is consistent with the sign immediately following
  * [Fix missing tab](https://github.com/n-takumasa/py-janaf/commit/196c788c792bb672f339d073a0d21c610fabff53)
    * NOTE: Based on [PDF files](https://janaf.nist.gov/pdf/JANAF-FourthEd-1998-Carbon.pdf#page=83)
  * [Ignore comment-like lines](https://github.com/n-takumasa/py-janaf/commit/d99b942fa8848eed8b8308cf9a50c1411a6f14bf)

## Usage

```
pip install janaf
```

```py
>>> import polars as pl
>>> import janaf
>>> table = janaf.search(formula="CO2$")
>>> table.name
'Carbon Dioxide (CO2)'
>>> table.formula
'C1O2(g)'
>>> table.df
shape: (62, 9)
┌────────┬────────┬─────────┬──────────────┬───┬───────────┬───────────┬─────────┬──────┐
│ T(K)   ┆ Cp     ┆ S       ┆ -[G-H(Tr)]/T ┆ … ┆ delta-f H ┆ delta-f G ┆ log Kf  ┆ Note │
│ ---    ┆ ---    ┆ ---     ┆ ---          ┆   ┆ ---       ┆ ---       ┆ ---     ┆ ---  │
│ f64    ┆ f64    ┆ f64     ┆ f64          ┆   ┆ f64       ┆ f64       ┆ f64     ┆ str  │
╞════════╪════════╪═════════╪══════════════╪═══╪═══════════╪═══════════╪═════════╪══════╡
│ 0.0    ┆ 0.0    ┆ 0.0     ┆ inf          ┆ … ┆ -393.151  ┆ -393.151  ┆ inf     ┆ null │
│ 100.0  ┆ 29.208 ┆ 179.009 ┆ 243.568      ┆ … ┆ -393.208  ┆ -393.683  ┆ 205.639 ┆ null │
│ 200.0  ┆ 32.359 ┆ 199.975 ┆ 217.046      ┆ … ┆ -393.404  ┆ -394.085  ┆ 102.924 ┆ null │
│ 298.15 ┆ 37.129 ┆ 213.795 ┆ 213.795      ┆ … ┆ -393.522  ┆ -394.389  ┆ 69.095  ┆ null │
│ …      ┆ …      ┆ …       ┆ …            ┆ … ┆ …         ┆ …         ┆ …       ┆ …    │
│ 5700.0 ┆ 64.68  ┆ 374.853 ┆ 317.953      ┆ … ┆ -417.658  ┆ -385.89   ┆ 3.536   ┆ null │
│ 5800.0 ┆ 64.772 ┆ 375.979 ┆ 318.944      ┆ … ┆ -418.541  ┆ -385.324  ┆ 3.47    ┆ null │
│ 5900.0 ┆ 64.865 ┆ 377.087 ┆ 319.92       ┆ … ┆ -419.445  ┆ -384.745  ┆ 3.406   ┆ null │
│ 6000.0 ┆ 64.957 ┆ 378.178 ┆ 320.882      ┆ … ┆ -420.372  ┆ -384.148  ┆ 3.344   ┆ null │
└────────┴────────┴─────────┴──────────────┴───┴───────────┴───────────┴─────────┴──────┘
>>> table.df.filter(pl.col("T(K)")==298.15).item(0, "delta-f H")  # kJ/mol
-393.522
```

## Credit

Following files are distributed in [NIST-JANAF Tables](https://janaf.nist.gov/):
* [py-janaf/janaf/janaf.json](https://github.com/n-takumasa/py-janaf/blob/main/janaf/janaf.json)
* [py-janaf/janaf/data/](https://github.com/n-takumasa/py-janaf/tree/main/janaf/data)

### [NIST-JANAF Tables - Credits](https://janaf.nist.gov/janbanr.html)

NIST Standard Reference Database 13

NIST JANAF THERMOCHEMICAL TABLES 1985
Version 1.0

Data compiled and evaluated by
M.W. Chase, Jr., C.A. Davies, J.R. Downey, Jr.
D.J. Frurip, R.A. McDonald, and A.N. Syverud

Distributed by
Standard Reference Data Program
National Institute of Standards and Technology
Gaithersburg, MD 20899

Copyright 1986 by
the U.S. Department of Commerce
on behalf of the United States. All rights reserved.

DISCLAIMER: NIST uses its best efforts to deliver a high quality copy of
the Database and to verify that the data contained therein have been
selected on the basis of sound scientific judgement. However, NIST makes
no warranties to that effect, and NIST shall not be liable for any damage
that may result from errors or omissions in the Database.
