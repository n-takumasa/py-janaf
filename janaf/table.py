from __future__ import annotations

import io
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import numpy as np
import pandas as pd


def _sign(x: str | float) -> int:
    if isinstance(x, str):
        return -1 if x[0] == "-" else 1
    else:
        return np.sign(x)


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
        df = (
            pd.read_csv(
                io.StringIO(self.raw), sep="\t+", header=0, skiprows=1, engine="python"
            )
            .replace("INFINITE", float("inf"))
            .astype(float, errors="ignore")
            .assign(Note="")
            # .set_index("T(K)")
        )
        if df["delta-f H"].dtype != float:
            cond = (
                df["delta-f H"].str.contains("<-->", na=False)
                + df["delta-f H"].str.contains("TRANSITION", na=False)
                + df["delta-f H"].str.contains("PRESSURE", na=False)
                + df["delta-f H"].str.contains("FUGACITY", na=False)
                + df["delta-f H"].str.contains("Cp", na=False)
                + df["delta-f H"].str.contains("UNDEFINED", na=False)
            ).astype(bool)
            df.loc[cond, "Note"] = df["delta-f H"][cond]
            df.loc[cond, "delta-f H"] = float("nan")
            cond = df["delta-f H"].str.contains(" ", na=False)
            if cond.sum() > 0:
                # NOTE Heuristic Fix
                # * データの区切りが tab でない場合がある
                # * 負号が欠損している場合がある
                # * 直後の符号と一致すると仮定する
                for curr, row in df[cond].iterrows():
                    succ = df.index[df.index.get_loc(curr) + 1]
                    dfH, dfG, logKf = map(float, row["delta-f H"].split())
                    df.at[curr, "delta-f H"] = _sign(df.at[succ, "delta-f H"]) * dfH
                    df.at[curr, "delta-f G"] = _sign(df.at[succ, "delta-f G"]) * dfG
                    df.at[curr, "log Kf"] = _sign(df.at[succ, "log Kf"]) * logKf
            df["delta-f H"] = df["delta-f H"].astype(float)
        return df.set_index("T(K)")
