from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

import bs4
from yarl import URL

from ..library import Library

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
            try:
                self.cache[tag.get_text()] = self.url_builder(
                    tag.attrs["href"]
                ).replace("%23", "#")
            except KeyError:
                pass

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


class LuaManual(Library):
    classname: ClassVar[str]
    lua_version: ClassVar[str]
    is_preset: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://www.lua.org"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name,
            URL(f"https://www.lua.org/manual/{self.lua_version}"),
            use_cache=use_cache,
        )

    async def fetch_icon(self) -> str | None:
        return await super().fetch_icon()

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self.url
        if url is None:
            raise ValueError("Local lua manuals are not supported")

        async with session.get(url) as res:
            raw_content: bytes = await res.content.read()

        parser = LuaManualParser(
            raw_content, partial(self._build_url, port=webserver_port)
        )

        self.cache = await asyncio.to_thread(parser.parse)


class Lua54(LuaManual):
    classname: ClassVar[str] = "Lua 5.4 Reference Manual"
    lua_version: ClassVar[str] = "5.4"
