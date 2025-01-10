
import aiohttp
import json
from plugin.libraries.qmk import QmkIndexReader


async def main() -> None:
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://docs.qmk.fm/assets/chunks/@localSearchIndexroot.DuIlbnO1.js") as res:
            reader = QmkIndexReader(await res.content.read())
        
        data = reader.parse_file()
        with open("data.json", "w", encoding="UTF-8") as f:
            f.write(data)
        print(json.loads(data))
        with open("data.json", "w", encoding="UTF-8") as f:
            json.dump(json.loads(data), f, indent=4)


import asyncio

asyncio.run(main())
