from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING

import bs4
import msgspec

from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets._structs.qmk import QmkLocalSearchData

if TYPE_CHECKING:
    from aiohttp import ClientSession

response_decoder = msgspec.json.Decoder(type=QmkLocalSearchData)

THEME_FILE_PARSER_PATTERN = re.compile(r"([^\"]+VPLocalSearchBox[^\"]+)")
SEARCHBOX_FILE_PARSER_PATTERN = re.compile(r"([^\"]+localSearchIndexroot[^\"]+)")


class QmkDocs(PresetLibrary, base_url="https://docs.qmk.fm"):
    def qmk_get_theme(self, text: bytes) -> list[str]:
        soup = bs4.BeautifulSoup(text.decode(), "html.parser")
        return [
            str(tag.attrs["href"])
            for tag in soup.find_all("link", rel="modulepreload")
            if isinstance(tag, bs4.Tag)
        ]

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

    async def find_match_from_url(
        self, session: ClientSession, *, url: str, pattern: re.Pattern[str]
    ) -> str | None:
        async with session.get(self.loc.with_path(url)) as res:
            raw_content = await res.content.read()

        for match in pattern.finditer(raw_content.decode()):
            return match.group(0)

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()
        tags = await asyncio.to_thread(self.qmk_get_theme, raw_content)

        for tag in tags:
            search_box_url = await self.find_match_from_url(
                session, url=tag, pattern=THEME_FILE_PARSER_PATTERN
            )
            if search_box_url is None:
                continue
            index_name = await self.find_match_from_url(
                session, url=search_box_url, pattern=SEARCHBOX_FILE_PARSER_PATTERN
            )
            if index_name is None:
                continue
            self.cache = await self.parse_index(
                session, index_name.strip("/"), webserver_port
            )
            return


preset = QmkDocs
