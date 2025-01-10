from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from yarl import URL

from ..library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession


class QmkLocalSearchField(msgspec.Struct):
    title: str
    titles: list[str]


class QmkLocalSearchData(msgspec.Struct):
    documentIds: dict[str, str]
    storedFields: dict[str, QmkLocalSearchField]


class QmkDocs(Library):
    inventory_url: ClassVar[str] = (
        "https://docs.qmk.fm/assets/chunks/@localSearchIndexroot.DuIlbnO1.js"
    )
    classname: ClassVar[str] = "docs.qmk.fm"
    is_preset: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://docs.qmk.fm"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, URL("https://docs.qmk.fm/"), use_cache=use_cache)

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.inventory_url) as res:
            raw_content: bytes = await res.content.read()

        line = raw_content.splitlines()[0].decode()
        raw_json = (
            line.removesuffix("`;")
            .removeprefix("const _localSearchIndexroot = `")
            .replace("\\`", "`")
        )

        index = msgspec.json.decode(raw_json, type=QmkLocalSearchData)
        cache = {}

        for docid, field in index.storedFields.items():
            document = index.documentIds[docid]
            cache[field.title] = self._build_url(document, webserver_port)

        self.cache = cache
