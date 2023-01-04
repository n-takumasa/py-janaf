from __future__ import annotations

import asyncio
import json
from pathlib import Path

import aiofiles
import aiohttp

root = Path(__file__).parent.parent.absolute()
path_json = root / "janaf/janaf.json"


def url(index: str) -> str:
    return f"https://janaf.nist.gov/tables/{index}.txt"


def dst(index: str) -> Path:
    return root / f"janaf/data/{index}.txt"


async def fetch(session: aiohttp.ClientSession, url: str, dst: Path):
    async with session.get(url) as res:
        data = await res.text("utf-8")
        async with aiofiles.open(dst, "w", encoding="utf-8") as f:
            await f.write(data)


async def main():
    with open(path_json, "r", encoding="utf-8") as fp:
        indexes = json.load(fp)["index"]

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[fetch(session, url(index), dst(index)) for index in indexes]
        )


if __name__ == "__main__":
    asyncio.run(main())
