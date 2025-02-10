from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

import msgspec
import yarl
from aiohttp import ClientSession

from ....entry import Entry

if TYPE_CHECKING:
    from collections.abc import Generator

    from aiohttp import ClientSession

    from ..structs import ApiIndex


class SearchHighlights(msgspec.Struct):
    title: list[str]
    content: list[str]
    content_explicit: list[str]


class SearchHit(msgspec.Struct):
    id: str
    url: str
    title: str
    breadcrumbs: str
    highlights: SearchHighlights


class SearchResponse(msgspec.Struct):
    hits: list[SearchHit]


class ErrorResponse(msgspec.Struct):
    error: str
    key: str


search_decoder = msgspec.json.Decoder(type=SearchResponse)
error_decoder = msgspec.json.Decoder(type=ErrorResponse)


class Github:
    def __init__(self, query: str, info: ApiIndex, session: ClientSession) -> None:
        self.session = session
        self.info = info
        self.query = query

    def __await__(self) -> Generator[Any, Any, dict[str, str | Entry]]:
        return self.__call__().__await__()

    async def __call__(self) -> dict[str, str | Entry]:
        url = yarl.URL(self.info.url)

        if not self.query:
            return {"Github Docs": str(url)}

        async with self.session.get(
            url, params={"query": self.query}, headers=self.info.headers
        ) as res:
            raw = await res.content.read()

        resp = search_decoder.decode(raw)

        return {
            hit.title: Entry(
                f"{hit.title} / {hit.breadcrumbs}",
                str(url.with_path(hit.url)),
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
