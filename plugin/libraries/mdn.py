from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from msgspec import json
from yarl import URL

from ..library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession


class DocEntry(msgspec.Struct):
    url: str
    title: str


class MdnDocs(Library):
    classname: ClassVar[str] = "developer.mozilla.org"
    is_preset: ClassVar[bool] = True

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name, URL("https://developer.mozilla.org/en-US"), use_cache=use_cache
        )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self.url
        if url is None:
            raise ValueError("Local mdndocs are not supported")

        async with session.get(url / "search-index.json") as res:
            raw_content: bytes = await res.content.read()

        with open("raw", "wb") as f:
            f.write(raw_content)

        data = json.decode(raw_content, type=list[DocEntry])

        self.cache = {
            entry.title: self._build_url(entry.url, webserver_port) for entry in data
        }
