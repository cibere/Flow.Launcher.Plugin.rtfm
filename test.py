
import aiohttp
import json
from plugin.libraries.ss64 import SS64Mac, SS64bash, SS64NT, SS64PS


async def main(doc) -> None:
    async with aiohttp.ClientSession() as cs:
        docs = doc("d", use_cache=True)
        await docs.build_cache(cs, 0)
    
    with open("cache.json", "w") as f:
        json.dump(docs.cache, f, indent=4)
    print(f"Done indexing {len(docs.cache)} entries")


import asyncio

asyncio.run(main(SS64Mac))
asyncio.run(main(SS64bash))
asyncio.run(main(SS64NT))
asyncio.run(main(SS64PS))