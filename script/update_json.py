from __future__ import annotations

import asyncio
from pathlib import Path

import aiohttp

url = "https://janaf.nist.gov/dat/janaf.json"
root = Path(__file__).parent.parent.absolute()
dst = root / "janaf/janaf.json"


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            text = await res.text("utf-8")
            with open(dst, "w", encoding="utf-8") as f:
                f.write(text)


if __name__ == "__main__":
    asyncio.run(main())
