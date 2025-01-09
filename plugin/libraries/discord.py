from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession
from yarl import URL

from ..library import Library

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
    objectID: str
    type: str
    hierarchy: SearchHitHierarchy


class SearchResult(msgspec.Struct):
    hits: list[SearchHit]


class SearchResponse(msgspec.Struct):
    results: list[SearchResult]


class Discord(Library):
    classname: ClassVar[str] = "discord.dev"
    is_preset: ClassVar[bool] = True
    is_api: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://discord.dev"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name,
            URL("https://discord.com/developers/docs"),
            use_cache=False,
        )

    async def make_request(self, session: ClientSession, query: str) -> None:
        url = "https://7tyoyf10z2-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for JavaScript (4.23.3); Browser (lite); docsearch (3.3.1); docsearch-react (3.3.1)&x-algolia-api-key=786517d17e19e9d306758dd276bc6574&x-algolia-application-id=7TYOYF10Z2"
        payload = {
            "requests": [
                {
                    "query": query,
                    "indexName": "discord",
                    "params": "attributesToRetrieve=%5B%22hierarchy.lvl0%22%2C%22hierarchy.lvl1%22%2C%22hierarchy.lvl2%22%2C%22hierarchy.lvl3%22%2C%22hierarchy.lvl4%22%2C%22hierarchy.lvl5%22%2C%22hierarchy.lvl6%22%2C%22content%22%2C%22type%22%2C%22url%22%5D&attributesToSnippet=%5B%22hierarchy.lvl1%3A10%22%2C%22hierarchy.lvl2%3A10%22%2C%22hierarchy.lvl3%3A10%22%2C%22hierarchy.lvl4%3A10%22%2C%22hierarchy.lvl5%3A10%22%2C%22hierarchy.lvl6%3A10%22%2C%22content%3A10%22%5D&snippetEllipsisText=%E2%80%A6&highlightPreTag=%3Cmark%3E&highlightPostTag=%3C%2Fmark%3E&hitsPerPage=20",
                }
            ]
        }
        async with session.post(url, json=payload) as res:
            raw = await res.content.read()

        resp = msgspec.json.decode(raw, type=SearchResponse)

        cache = {}

        for result in resp.results:
            for hit in result.hits:
                cache[hit.hierarchy.to_text()] = hit.url

        self.cache = cache
