from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession

from .preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class SearchHitHierarchy(msgspec.Struct):
    lvl0: str | None
    lvl1: str | None
    lvl2: str | None
    lvl3: str | None
    lvl4: str | None
    lvl5: str | None
    lvl6: str | None

    def to_text(self) -> str:
        return " - ".join(
            [
                lvl
                for lvl in reversed(
                    (
                        self.lvl0,
                        self.lvl1,
                        self.lvl2,
                        self.lvl3,
                        self.lvl4,
                        self.lvl5,
                        self.lvl6,
                    )
                )
                if lvl is not None
            ]
        )


class SearchHit(msgspec.Struct):
    url: str
    hierarchy: SearchHitHierarchy


class SearchResult(msgspec.Struct):
    hits: list[SearchHit]


class SearchResponse(msgspec.Struct):
    results: list[SearchResult]


response_decoder = msgspec.json.Decoder(type=SearchResponse)
Jsonable = dict[str, "Jsonable"] | list["Jsonable"] | int | str


class AlgoliaConfig(msgspec.Struct):
    url: str
    index_name: str
    kwargs: dict[str, Jsonable] = {}


class AlgoliaBase(PresetLibrary):
    is_preset: ClassVar[bool] = True
    is_api: ClassVar[bool] = True
    algolia_config: ClassVar[AlgoliaConfig]

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, use_cache=False)

    def __init_subclass__(
        cls,
        config: AlgoliaConfig,
        base_url: str | None = None,
        favicon_url: str | None = None,
    ) -> None:
        cls.algolia_config = config
        return super().__init_subclass__(base_url, favicon_url)

    async def make_request(self, session: ClientSession, query: str) -> None:
        payload = {
            "requests": [
                {
                    "query": query,
                    "indexName": self.algolia_config.index_name,
                }
                | self.algolia_config.kwargs
            ]
        }
        async with session.post(self.algolia_config.url, json=payload) as res:
            raw = await res.content.read()

        resp = response_decoder.decode(raw)

        cache = {}

        for result in resp.results:
            for hit in result.hits:
                cache[hit.hierarchy.to_text()] = hit.url

        self.cache = cache
