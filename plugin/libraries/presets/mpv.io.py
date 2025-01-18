from __future__ import annotations

import asyncio
import re
from functools import partial
from typing import TYPE_CHECKING, Callable

import bs4

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class MpvIoParser:
    def __init__(self, data: bytes, url_builder: Callable[[str], str]) -> None:
        self.data = data
        self.soup = bs4.BeautifulSoup(data, "html.parser")
        self.cache: dict[str, str] = {}
        self.url_builder = url_builder

    def header_to_fragment(self, header: str) -> str:
        return "#" + header.lower().replace(" ", "-")

    def parse(
        self,
    ) -> None:
        headers: list[bs4.Tag] = self.soup.find_all(re.compile("^h[1-6]$"))

        for header in headers:
            self.cache[header.text] = self.url_builder(
                self.header_to_fragment(header.text)
            )


class MpvIoBase(PresetLibrary, is_variant=True):
    def __init_subclass__(cls, version: str) -> None:
        return super().__init_subclass__(base_url=f"https://mpv.io/manual/{version}")

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()

        parser = MpvIoParser(raw_content, partial(self._build_url, port=webserver_port))

        await asyncio.to_thread(parser.parse)
        self.cache = parser.cache


class MpvIoLatest(MpvIoBase, version="master"): ...


class MpvIoStable(MpvIoBase, version="stable"): ...


presets = (MpvIoLatest, MpvIoStable)
