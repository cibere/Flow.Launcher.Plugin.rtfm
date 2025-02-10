from __future__ import annotations

from typing import TYPE_CHECKING, Any

from msgspec import Struct, json
from yarl import URL

from ....entry import Entry

if TYPE_CHECKING:
    from collections.abc import Generator

    from aiohttp import ClientSession

    from ..structs import ApiIndex


class Suggestion(Struct):
    title: list[str]
    summary: list[str]
    product: str
    shortName: str
    pageId: str
    path: str
    type: str

    @property
    def label(self) -> str:
        return f"{''.join(self.title)} - {''.join(self.summary)}"


class Page(Struct):
    header: str
    type: str
    more: int
    q: str
    suggestions: list[Suggestion]


class Response(Struct):
    searchtext: str
    pages: list[Page]


response_decoder = json.Decoder(type=Response)


class Mathworks:
    def __init__(self, query: str, info: ApiIndex, session: ClientSession) -> None:
        self.session = session
        self.info = info
        self.query = query

    def __await__(self) -> Generator[Any, Any, dict[str, str | Entry]]:
        return self.__call__().__await__()

    async def __call__(self) -> dict[str, Entry | str]:
        url = URL(self.info.url)

        if not self.query.strip():
            return {"Index Page": str(url.with_path("help"))}

        params = {"q": self.query} | self.info.options

        async with self.session.get(
            url, params=params, raise_for_status=True, headers=self.info.headers
        ) as res:
            raw = await res.content.read()

        resp = response_decoder.decode(raw)

        cache = {}

        for page in resp.pages:
            for entry in page.suggestions:
                cache[entry.label] = Entry(
                    entry.label,
                    url=str(url / "help" / entry.path),
                    options={"sub": f"type: {entry.type} | {entry.product}"},
                )

        return cache
