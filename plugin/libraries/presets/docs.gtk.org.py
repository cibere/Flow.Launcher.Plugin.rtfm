from __future__ import annotations

from typing import TYPE_CHECKING

from msgspec import json

from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.gtk import GtkIndex

if TYPE_CHECKING:
    from aiohttp import ClientSession

index_decoder = json.Decoder(type=GtkIndex)


class GtkDocBase(PresetLibrary):
    version: str

    def __init_subclass__(cls, version: str) -> None:
        cls.version = version
        return super().__init_subclass__(
            base_url=f"https://docs.gtk.org/{version}",
            favicon_url="https://docs.gtk.org",
            is_variant=True,
        )

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


class Gtk3Docs(GtkDocBase, version="gtk3"): ...


class Gtk4Docs(GtkDocBase, version="gtk4"): ...


presets = (
    Gtk3Docs,
    Gtk4Docs,
)
