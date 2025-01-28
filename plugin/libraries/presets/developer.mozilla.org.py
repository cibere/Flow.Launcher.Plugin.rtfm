from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec
from msgspec import json

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from yarl import URL


class DocEntry(msgspec.Struct):
    url: str
    title: str


doc_entry_decoder = json.Decoder(type=list[DocEntry])


class MdnDocs(PresetLibrary, base_url="https://developer.mozilla.org"):
    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url / "en-US" / "search-index.json") as res:
            raw_content: bytes = await res.content.read()

        data = doc_entry_decoder.decode(raw_content)

        self.cache = {
            entry.title: self._build_url(entry.url, webserver_port) for entry in data
        }

    @classmethod
    def validate_url(cls, url: URL) -> bool:
        return url.host == "developer.mozilla.org"


preset = MdnDocs
