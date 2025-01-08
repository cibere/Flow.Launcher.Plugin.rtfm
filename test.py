import aiohttp

from plugin.libraries.qmk import QmkDocs


async def main() -> None:
    async with aiohttp.ClientSession() as cs:
        lib = QmkDocs("v2", use_cache=True)
        await lib.build_cache(cs, 0)
    with open("cache.json", "w") as f:
        import json
        json.dump(lib.cache, f)

import asyncio

asyncio.run(main())
