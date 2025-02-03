from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable

import bs4

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from bs4._typing import _QueryResults


class LuaManualParser:
    def __init__(self, data: bytes, url_builder: Callable[[str], str]) -> None:
        self.data = data
        self.soup = bs4.BeautifulSoup(data, "html.parser")
        self.cache: dict[str, str] = {}
        self.url_builder = url_builder

    def parse_atags(self, tags: _QueryResults) -> None:
        for tag in tags:
            if not isinstance(tag, bs4.Tag):
                continue

            href = tag.attrs.get("href")
            if href:
                self.cache[tag.get_text()] = self.url_builder(str(href)).replace(
                    "%23", "#"
                )

    def parse_nav(self) -> None:
        container = self.soup.find_all("ul", class_="contents menubar")[0]
        if isinstance(container, bs4.Tag):
            self.parse_atags(container.find_all("a"))

    def parse_index(self) -> None:
        container = self.soup.find_all("table", class_="menubar")[0]
        if isinstance(container, bs4.Tag):
            self.parse_atags(container.find_all("a"))

    def parse(
        self,
    ) -> dict[str, str]:
        self.parse_nav()
        self.parse_index()
        return self.cache


class LuaManual(PresetLibrary, is_variant=True, favicon_url="https://www.lua.org"):
    def __init_subclass__(cls, version: int | float) -> None:
        return super().__init_subclass__(
            base_url=f"https://www.lua.org/manual/{version}",
        )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()

        parser = LuaManualParser(
            raw_content, partial(self._build_url, port=webserver_port)
        )

        self.cache = await asyncio.to_thread(parser.parse)


class Lua54(LuaManual, version=5.4): ...


preset = Lua54
