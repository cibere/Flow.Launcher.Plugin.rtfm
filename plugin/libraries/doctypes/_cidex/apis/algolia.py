from __future__ import annotations

from typing import TYPE_CHECKING, Any

from msgspec import Struct, json

if TYPE_CHECKING:
    from collections.abc import Generator

    from aiohttp import ClientSession

    from ....entry import Entry
    from ..structs import ApiIndex


class SearchHitHierarchy(Struct):
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


class SearchHit(Struct):
    url: str
    hierarchy: SearchHitHierarchy


class SearchResult(Struct):
    hits: list[SearchHit]


class SearchResponse(Struct):
    results: list[SearchResult]


response_decoder = json.Decoder(type=SearchResponse)


class Algolia:
    def __init__(self, query: str, info: ApiIndex, session: ClientSession) -> None:
        self.session = session
        self.info = info
        self.query = query

    def __await__(self) -> Generator[Any, Any, dict[str, str | Entry]]:
        return self.__call__().__await__()

    async def __call__(self) -> dict[str, str | Entry]:
        payload = {
            "requests": [
                {
                    "query": self.query,
                }
                | self.info.options
            ]
        }
        async with self.session.post(
            self.info.url, json=payload, headers=self.info.headers
        ) as res:
            raw = await res.content.read()

        resp = response_decoder.decode(raw)

        cache = {}

        for result in resp.results:
            for hit in result.hits:
                cache[hit.hierarchy.to_text()] = hit.url

        return cache
