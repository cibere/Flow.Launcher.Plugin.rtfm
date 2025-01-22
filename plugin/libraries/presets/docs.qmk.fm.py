from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import bs4
import msgspec

from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.qmk import QmkLocalSearchData

if TYPE_CHECKING:
    from aiohttp import ClientSession

response_decoder = msgspec.json.Decoder(type=QmkLocalSearchData)


class QmkDocs(PresetLibrary, base_url="https://docs.qmk.fm"):
    def qmk_get_theme(self, text: bytes) -> list[str]:
        soup = bs4.BeautifulSoup(text.decode(), "html.parser")
        return [tag.attrs["href"] for tag in soup.find_all("link", rel="modulepreload")]

    async def qmk_parse_theme_file(
        self, session: ClientSession, url: str
    ) -> str | None:
        async with session.get(self.loc.with_path(url)) as res:
            raw_content = await res.content.read()
        data = raw_content.decode()
        if not data.startswith("const __vite__fileDeps=["):
            return
        return data.removeprefix('const __vite__fileDeps=["').split('"')[0]

    async def qmk_parse_search_box_file(
        self, session: ClientSession, url: str
    ) -> str | None:
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
        async with session.get(self.loc / "assets" / "chunks" / filename) as res:
            raw_content = await res.content.read()

        line = raw_content.splitlines()[0].decode()
        raw_json = (
            line.removesuffix("`;")
            .removeprefix("const _localSearchIndexroot = `")
            .replace("\\`", "`")
        )

        index = response_decoder.decode(raw_json)
        cache = {}

        for docid, field in index.storedFields.items():
            document = index.documentIds[docid]
            cache[field.title] = self._build_url(document, webserver_port)

        return cache

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()
        tags = await asyncio.to_thread(self.qmk_get_theme, raw_content)

        for tag in tags:
            search_box_url = await self.qmk_parse_theme_file(session, tag)
            if search_box_url is None:
                continue
            index_name = await self.qmk_parse_search_box_file(session, search_box_url)
            if index_name is None:
                continue
            self.cache = await self.parse_index(
                session, index_name.strip("/"), webserver_port
            )
            return


preset = QmkDocs
