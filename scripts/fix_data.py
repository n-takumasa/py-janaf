from __future__ import annotations

import csv
import io
import logging
import re
from pathlib import Path


def fix_missing_tab(text: str) -> str:
    # eg. C-083.txt
    # 288.5001548.088	111.062	118.520	-2.152	II <--> III
    #       ^^ : missing tab

    if re.search(r"\.\d+\.", text.split("\n", 1)[1]) is None:
        return text

    return re.sub(r"(\.\d{3})(\d)", r"\1\t\2", text)


def trim_comment(text: str) -> str:
    # eg. S-021.txt
    # 1000	180.064	638.302	516.162	122.140	-392.026	52.900	-2.763
    # H
    # 1100	180.552	655.488	528.059	140.172	-388.966	97.243	-4.618

    title, header, body = text.split("\n", 2)

    new_body = (
        "\n".join(line for line in body.splitlines() if line[None:1] != "H") + "\n"
    )
    return f"{title}\n{header}\n{new_body}"


def combine_note(text: str) -> str:
    # eg. Ba-001.txt
    # 582.530	54.400	87.232	68.471	10.929	ALPHA <--> BETA
    # +
    # 582.530	32.468	87.232	68.471	10.929	TRANSITION

    title, header, body = text.split("\n", 2)

    if "+" not in body:
        return text

    lines = body.splitlines()
    for i in range(len(lines)):
        if "+" != lines[i][0]:
            continue

        if (r := re.search(r"\t([^\t]+)$", lines[i + 1])) is None:
            raise NotImplementedError
        target = r.group(1)
        lines[i - 1] = f"{lines[i-1]} {target}"
        lines[i] = ""
        lines[i + 1] = lines[i + 1].replace(target, "")

    new_body = "\n".join(x for x in lines if x != "").replace("\n\n", "\n") + "\n"
    return f"{title}\n{header}\n{new_body}"


def fix_missing_sign(text: str) -> str:
    # eg. Al-002.txt
    # 933.450	32.959	59.738	40.474	17.982	CRYSTAL <--> LIQUID
    # 1000	34.358	62.055	41.834	20.221	10.585 0.760  0.040
    #                                      ^             ^ : missing sign
    # 1100	36.722	65.438	43.827	23.772	-10.209	1.878	-0.089

    title, header, body = text.split("\n", 2)

    cell = [
        row
        for row in csv.reader(
            body.splitlines(),
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
        )
    ]

    for i in range(len(cell) - 1):
        if (
            cell[i][5][None:1]
            in {"", "-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
            and " " in cell[i][5]
        ):
            assert len(cell[i]) == 6
            idx = i + 1
            while len(cell[idx]) != 8:
                idx += 1
            cell[i].extend(["", ""])
            h, g, kf = cell[i][5].split()
            cell[i][5] = f"{'-' if cell[idx][5][None:1] == '-' else ''}{h}"
            cell[i][6] = f"{'-' if cell[idx][6][None:1] == '-' else ''}{g}"
            cell[i][7] = f"{'-' if cell[idx][7][None:1] == '-' else ''}{kf}"

    with io.StringIO() as f:
        writer = csv.writer(
            f,
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
            lineterminator="\n",
        )
        writer.writerows(cell)
        new_body = f.getvalue()

    return f"{title}\n{header}\n{new_body}"


def fix_inf(text: str) -> str:
    # eg. Al-001.txt
    # 0	0.	0.	INFINITE	-4.539	0.	0.	0.
    #           ^^^^^^^^
    title, header, body = text.split("\n", 2)

    new_body = body.replace("INFINITE", "+inf")
    return f"{title}\n{header}\n{new_body}"


def main() -> None:
    for fp in Path("src/janaf/data/").glob("*.txt"):
        orig = fp.read_text(encoding="ascii")
        text = orig
        try:
            text = fix_missing_tab(text)
            text = trim_comment(text)
            text = combine_note(text)
            text = fix_missing_sign(text)
            text = fix_inf(text)
        except:
            logging.error(fp)
            raise
        if text != orig:
            logging.info(f"fixed: {fp}")
            fp.write_text(text, encoding="ascii")


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    main()
