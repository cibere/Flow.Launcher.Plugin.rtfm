
import aiohttp
import json
from plugin.libraries.qmk import QmkDocs


async def main() -> None:
    async with aiohttp.ClientSession() as cs:
        docs = QmkDocs("d", use_cache=True)
        await docs.build_cache(cs, 0)
    
    with open("cache.json", "w") as f:
        json.dump(docs.cache, f, indent=4)


import asyncio

asyncio.run(main())
