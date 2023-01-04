import io
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class Table:
    index: str

    @cached_property
    def fname(self):
        return Path(__file__).parent / f"data/{self.index}.txt"

    @cached_property
    def raw(self):
        with open(self.fname, "r", encoding="utf-8") as f:
            return f.read()

    @cached_property
    def name(self):
        return self.raw.split("\n", 1)[0].split("\t", 1)[0]

    @cached_property
    def formula(self):
        return self.raw.split("\n", 1)[0].split("\t", 1)[1]

    @cached_property
    def df(self):
        return (
            pd.read_csv(io.StringIO(self.raw), delimiter="\t", skiprows=1)
            .replace("INFINITE", float("nan"))
            .astype(float, errors="ignore")
            # .dropna(axis="index")
            .set_index("T(K)")
        )
