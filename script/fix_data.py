from __future__ import annotations

import re
from pathlib import Path


def fix(fp: Path) -> bool:
    with fp.open("r+") as f:
        orig = f.read()
        result = orig
        result = fix_missing_tab(result)
        result = fix_space_to_tab(result)
    if orig == result:
        return False
    with fp.open("w") as f:
        f.write(result)
        return True


def fix_missing_tab(text: str) -> str:
    # eg. C-083.txt
    # 288.5001548.088	111.062	118.520	-2.152	II <--> III
    #       ^^ : missing tab
    if re.search(r"\.\d+\.", text) is None:
        return text
    return re.sub(r"(\.\d{3})(\d)", r"\1\t\2", text)


def fix_space_to_tab(text: str) -> str:
    if re.search(r"\d +\d", text) is None:
        return text
    return re.sub(r"(\d) +(\d)", r"\1\t\2", text)


def main():
    for fp in Path("janaf/data/").glob("*.txt"):
        if fix(fp):
            print("Fixed:", fp)


if __name__ == "__main__":
    main()
