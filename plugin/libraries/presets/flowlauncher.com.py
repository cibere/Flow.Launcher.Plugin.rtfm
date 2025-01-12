from __future__ import annotations

from typing import TYPE_CHECKING

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class FlowLauncherDocs(PresetLibrary, base_url="https://www.flowlauncher.com/docs"):
    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get("https://www.flowlauncher.com/docs/_sidebar.md") as res:
            raw_content: bytes = await res.content.read()

        lines = raw_content.decode().splitlines()
        header = None

        cache = {}

        for line in lines:
            line = line.strip("-    ")
            if not line.startswith("[**"):
                header = line
            else:
                parts = line.split("**](/")
                name = parts[0].strip("*[]")
                loc = parts[1].strip("()")

                title = f"{name} - {header}" if header else name
                cache[title] = self._build_url(loc, webserver_port)

        self.cache = cache


preset = FlowLauncherDocs
