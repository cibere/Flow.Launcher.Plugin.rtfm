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


class DiscordSex(Library):
    classname: ClassVar[str] = "discord.sex"
    is_preset: ClassVar[bool] = True
    is_api: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://docs.discord.sex"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name,
            URL("https://docs.discord.sex"),
            use_cache=False,
        )

    async def make_request(self, session: ClientSession, query: str) -> None:
        # replicate the way discord.sex's search engine makes the requests

        url = "https://jajudfjbi4-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for JavaScript (5.12.0); Lite (5.12.0); Browser; docsearch (3.6.3); docsearch-react (3.6.3)&x-algolia-api-key=13092021a31a84e0e8676c10affb9a16&x-algolia-application-id=JAJUDFJBI4"
        payload = {
            "requests": [
                {
                    "query": query,
                    "indexName": "discord-usercers",
                    "attributesToRetrieve": [
                        "hierarchy.lvl0",
                        "hierarchy.lvl1",
                        "hierarchy.lvl2",
                        "hierarchy.lvl3",
                        "hierarchy.lvl4",
                        "hierarchy.lvl5",
                        "hierarchy.lvl6",
                        "content",
                        "type",
                        "url",
                    ],
                    "attributesToSnippet": [
                        "hierarchy.lvl1:10",
                        "hierarchy.lvl2:10",
                        "hierarchy.lvl3:10",
                        "hierarchy.lvl4:10",
                        "hierarchy.lvl5:10",
                        "hierarchy.lvl6:10",
                        "content:10",
                    ],
                    "snippetEllipsisText": "…",
                    "highlightPreTag": "<mark>",
                    "highlightPostTag": "</mark>",
                    "hitsPerPage": 20,
                    "clickAnalytics": True,
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
