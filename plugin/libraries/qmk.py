from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, ClassVar

import bs4
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
    classname: ClassVar[str] = "docs.qmk.fm"
    is_preset: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://docs.qmk.fm"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, URL("https://docs.qmk.fm/"), use_cache=use_cache)

    def qmk_get_theme(self, text: bytes) -> list[str]:
        soup = bs4.BeautifulSoup(text.decode(), "html.parser")
        return [tag.attrs["href"] for tag in soup.find_all("link", rel="modulepreload")]

    async def qmk_parse_theme_file(
        self, session: ClientSession, url: str
    ) -> str | None:
        assert isinstance(self.loc, URL)

        async with session.get(self.loc.with_path(url)) as res:
            raw_content = await res.content.read()
        data = raw_content.decode()
        if not data.startswith("const __vite__fileDeps=["):
            return
        data = data.removeprefix('const __vite__fileDeps=["').split('"')[0]
        assert "VPLocalSearchBox" in data
        return data

    async def qmk_parse_search_box_file(
        self, session: ClientSession, url: str
    ) -> str | None:
        assert isinstance(self.loc, URL)

        async with session.get(self.loc.with_path(url)) as res:
            raw_content = await res.content.read()
        data = raw_content.decode()

        for line in data.splitlines():
            if not line.startswith(
                'const localSearchIndex = { "root": () => __vitePreload(() => import'
            ):
                continue

            return line.removeprefix(
                'const localSearchIndex = { "root": () => __vitePreload(() => import(".'
            ).split('"')[0]

    async def parse_index(
        self, session: ClientSession, filename: str, webserver_port: int
    ) -> dict[str, str]:
        assert isinstance(self.loc, URL)

        async with session.get(self.loc / "assets" / "chunks" / filename) as res:
            raw_content = await res.content.read()

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

        return cache

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        assert isinstance(self.loc, URL)

        async with session.get(self.loc) as res:
            raw_content: bytes = await res.content.read()
        tags = await asyncio.to_thread(self.qmk_get_theme, raw_content)

        for tag in tags:
            search_box_url = await self.qmk_parse_theme_file(session, tag)
            print(f"{search_box_url=}")
            if search_box_url is None:
                continue
            index_name = await self.qmk_parse_search_box_file(session, search_box_url)
            print(f"{index_name=}")
            if index_name is None:
                continue
            self.cache = await self.parse_index(
                session, index_name.strip("/"), webserver_port
            )
            return
