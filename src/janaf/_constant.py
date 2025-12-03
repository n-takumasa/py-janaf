from types import MappingProxyType

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
