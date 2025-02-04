from __future__ import annotations

import html
import logging
from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession

from plugin.libraries.entry import Entry
from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.github import ErrorResponse, SearchResponse

if TYPE_CHECKING:
    from aiohttp import ClientSession

log = logging.getLogger(__name__)

search_decoder = msgspec.json.Decoder(type=SearchResponse)
error_decoder = msgspec.json.Decoder(type=ErrorResponse)


class Github(
    PresetLibrary,
    base_url="https://docs.github.com",
    favicon_url="https://github.com/favicon.ico",
):
    is_preset: ClassVar[bool] = True
    is_api: ClassVar[bool] = True

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, use_cache=False)

    async def make_request(self, session: ClientSession, query: str) -> None:
        params = {"query": query}
        async with session.get(
            "https://docs.github.com/api/search/v1", params=params
        ) as res:
            raw = await res.content.read()

        try:
            resp = search_decoder.decode(raw)
        except msgspec.ValidationError:
            error = error_decoder.decode(raw)
            log.exception("Received error from github: %r", error)
            self.cache = {}
            return

        self.cache = {
            hit.title: Entry(
                f"{hit.title} / {hit.breadcrumbs}",
                self._build_url(hit.url, 0),
                {
                    "sub": html.unescape(
                        hit.highlights.content[0]
                        .replace("<mark>", "")
                        .replace("</mark>", "")
                        .replace("\n", " ")
                    )
                },
            )
            for hit in resp.hits
        }


preset = Github
