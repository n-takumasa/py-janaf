from __future__ import annotations

import re
from pathlib import Path


def fix(fp: Path) -> bool:
    with fp.open("r+") as f:
        orig = f.read()
        text = orig.split("\n", 1)[1]
        # eg. C-083.txt
        # 288.5001548.088	111.062	118.520	-2.152	II <--> III
        #       ^^ : missing tab
        if re.search(r"\.\d+\.", text) is None:
            return False
        f.seek(0)
        f.write(re.sub(r"(\.\d{3})(\d)", r"\1\t\2", orig))
        return True


def main():
    for fp in Path("janaf/data/").glob("*.txt"):
        if fix(fp):
            print("Fixed:", fp)


if __name__ == "__main__":
    main()
