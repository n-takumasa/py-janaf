from __future__ import annotations

import asyncio
from pathlib import Path

import aiofiles
import aiohttp

url = "https://janaf.nist.gov/dat/janaf.json"
root = Path(__file__).parent.parent.absolute()
dst = root / "src/janaf/janaf.json"


async def main() -> None:
    async with aiohttp.ClientSession() as session, session.get(url) as res:
        text = await res.text("utf-8")
        async with aiofiles.open(dst, "w", encoding="utf-8") as f:
            await f.write(text)


if __name__ == "__main__":
    asyncio.run(main())
