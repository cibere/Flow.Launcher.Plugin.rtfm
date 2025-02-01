from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from plugin.libraries.doctypes._structs.gidocgen import GiDocGenIndex
from plugin.libraries.library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from yarl import URL
import msgspec

index_decoder = msgspec.json.Decoder(type=GiDocGenIndex)


class Gidocgen(Library):
    typename: ClassVar[str] = "Gidocgen"

    if TYPE_CHECKING:
        url: URL  # type: ignore

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url / "index.json") as res:
            raw_content: bytes = await res.content.read()

        data = index_decoder.decode(raw_content)
        cache = {}

        for entry in data.symbols:
            label = entry.build_label()
            href = entry.href or f"{label}.html"
            url = self.url / href

            cache[label] = str(url)

        self.cache = cache


doctype = Gidocgen
