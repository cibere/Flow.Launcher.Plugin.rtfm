from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession

from plugin.libraries.entry import Entry
from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.mathworks import Response

if TYPE_CHECKING:
    from aiohttp import ClientSession

response_decoder = msgspec.json.Decoder(type=Response)


class MathWorksDoc(
    PresetLibrary,
    base_url="https://www.mathworks.com/help",
    favicon_url="https://www.mathworks.com/favicon.ico",
):
    is_preset: ClassVar[bool] = True
    is_api: ClassVar[bool] = True

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, use_cache=False)

    async def make_request(self, session: ClientSession, query: str) -> None:
        if not query.strip():
            self.cache = {"Index Page": "https://www.mathworks.com/help/"}
            return

        url = "https://www.mathworks.com/help/search/suggest/doccenter/en/R2024b"
        params = {"q": query, "selectedsource": "mw", "width": "785.667"}
        headers = {"User-Agent": "python-flow.launcher.plugin.rtfm/1.0.0"}

        async with session.get(
            url, headers=headers, params=params, raise_for_status=True
        ) as res:
            raw = await res.content.read()

        resp = response_decoder.decode(raw)

        cache = {}

        for page in resp.pages:
            for entry in page.suggestions:
                cache[entry.label] = Entry(
                    entry.label,
                    url=str(self.base_url / entry.path),
                    options={"sub": f"type: {entry.type} | {entry.product}"},
                )

        self.cache = cache


preset = MathWorksDoc
