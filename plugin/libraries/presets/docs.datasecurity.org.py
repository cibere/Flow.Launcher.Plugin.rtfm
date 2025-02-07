from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec
from flogin.utils import MISSING

from plugin.libraries.entry import Entry
from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.datasecurity import HeaderEntry, Response

if TYPE_CHECKING:
    from aiohttp import ClientSession

decoder = msgspec.json.Decoder(type=Response)


class DataSecurityDocs(
    PresetLibrary,
    favicon_url="https://docs.datasecurity.org/images/favicon.png",
    base_url="https://docs.datasecurity.org",
):
    def build_entries(
        self, headers: list[HeaderEntry], parents: list[str] = MISSING
    ) -> dict[str, Entry]:
        if not headers:
            return {}

        parents = parents or []
        cache = {}

        for header in headers:
            parts = [header.title, *parents]
            label = " - ".join(parts)

            cache[label] = Entry(label, self._build_url(header.link, 0))
            cache.update(self.build_entries(header.children, parts))

        return cache

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url / "assets/index.html-cf1f0bed.js") as res:
            raw_content = await res.content.read()

        stripped = (
            raw_content.strip()
            .removeprefix(b"const e=JSON.parse('")
            .removesuffix(b"');export{e as data};")
        )
        data = decoder.decode(stripped)

        self.cache = self.build_entries(data.headers)


preset = DataSecurityDocs
