
import aiohttp
import json
from plugin.libraries.discordsex import DiscordSex


async def main() -> None:
    async with aiohttp.ClientSession() as cs:
        sex = DiscordSex('sex', use_cache=True)
        await sex.make_request(cs, "test")
    
    formatted = json.dumps(sex.cache, indent=4)
    with open("cache.json", "w") as f:
        
        f.write(formatted)
    print(formatted)
    

import asyncio

asyncio.run(main())
