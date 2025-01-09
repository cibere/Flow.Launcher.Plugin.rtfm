from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from yarl import URL

from ..library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession


class FlowLauncherDocs(Library):
    inventory_url: ClassVar[str] = "https://www.flowlauncher.com/docs/_sidebar.md"
    classname: ClassVar[str] = "flowlauncher.com"
    is_preset: ClassVar[bool] = True

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name, URL("https://www.flowlauncher.com/docs/"), use_cache=use_cache
        )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.inventory_url) as res:
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
