import requests
u = "https://docs.astral.sh/ruff/search/search_index.json"
r = requests.get(u)
with open("data.json", "w") as f:
    import json
    json.dump(r.json(), f, indent=4)
quit()

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
