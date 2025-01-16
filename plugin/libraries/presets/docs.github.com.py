from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession

from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.github import ErrorResponse, SearchResponse

if TYPE_CHECKING:
    from aiohttp import ClientSession

log = logging.getLogger(__name__)


class Github(
    PresetLibrary,
    base_url="https://docs.github.com",
    favicon_url="https://github.com",
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
            resp = msgspec.json.decode(raw, type=SearchResponse)
        except msgspec.ValidationError:
            error = msgspec.json.decode(raw, type=ErrorResponse)
            log.exception(f"Received error from github: {error!r}")
            self.cache = {}
            return

        cache = {}

        for hit in resp.hits:
            cache[hit.title] = self._build_url(hit.url, 0)

        self.cache = cache


preset = Github
