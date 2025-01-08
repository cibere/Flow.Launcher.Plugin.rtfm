from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec
from msgspec import json

from ..library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession


class DocEntry(msgspec.Struct):
    location: str
    text: str
    title: str


class SearchIndexFile(msgspec.Struct):
    config: dict
    docs: list[DocEntry]


class Mkdocs(Library):
    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self.url
        if url is None:
            raise ValueError("Local mkdocs are not supported")

        async with session.get(url / "search" / "search_index.json") as res:
            raw_content: bytes = await res.content.read()

        data = json.decode(raw_content, type=SearchIndexFile)

        self.cache = {
            entry.title: self._build_url(entry.location, webserver_port)
            for entry in data.docs
        }
