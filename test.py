
import aiohttp
import json
from plugin.libraries.lua import Lua54


async def main() -> None:
    async with aiohttp.ClientSession() as cs:
        lib = Lua54("Lua54", use_cache=True)
        await lib.build_cache(cs, 0)
    
    formatted = json.dumps(lib.cache, indent=4)
    with open("cache.json", "w") as f:
        
        f.write(formatted)
    print(formatted)
    

import asyncio

asyncio.run(main())
