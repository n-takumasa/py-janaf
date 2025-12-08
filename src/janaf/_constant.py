from types import MappingProxyType
from typing import Literal

UNITS_MAPPING = MappingProxyType(
    {
        "T(K)": "K",
        "Cp": "J/K/mol",
        "S": "J/K/mol",
        "-[G-H(Tr)]/T": "J/K/mol",
        "H-H(Tr)": "kJ/mol",
        "delta-f H": "kJ/mol",
        "delta-f G": "kJ/mol",
        "log Kf": "",
    }
)

ColumnsType = Literal[
    "T(K)",
    "Cp",
    "S",
    "-[G-H(Tr)]/T",
    "H-H(Tr)",
    "delta-f H",
    "delta-f G",
    "log Kf",
]
