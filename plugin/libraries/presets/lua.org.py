from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable

import bs4

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class LuaManualParser:
    def __init__(self, data: bytes, url_builder: Callable[[str], str]) -> None:
        self.data = data
        self.soup = bs4.BeautifulSoup(data, "html.parser")
        self.cache: dict[str, str] = {}
        self.url_builder = url_builder

    def parse_atags(self, tags: list[bs4.Tag]) -> None:
        for tag in tags:
            href = tag.attrs.get("href")
            if href:
                self.cache[tag.get_text()] = self.url_builder(href).replace("%23", "#")

    def parse_nav(self) -> None:
        container: bs4.Tag = self.soup.find_all("ul", class_="contents menubar")[0]
        self.parse_atags(container.find_all("a"))

    def parse_index(self) -> None:
        container: bs4.Tag = self.soup.find_all("table", class_="menubar")[0]
        self.parse_atags(container.find_all("a"))

    def parse(
        self,
    ) -> dict[str, str]:
        self.parse_nav()
        self.parse_index()
        return self.cache


class LuaManual(PresetLibrary):
    def __init_subclass__(cls, version: int | float) -> None:
        return super().__init_subclass__(
            base_url=f"https://www.lua.org/manual/{version}",
            favicon_url="https://www.lua.org",
        )

    async def fetch_icon(self) -> str | None:
        return await super().fetch_icon()

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()

        parser = LuaManualParser(
            raw_content, partial(self._build_url, port=webserver_port)
        )

        self.cache = await asyncio.to_thread(parser.parse)


class Lua54(LuaManual, version=5.4): ...


preset = Lua54
