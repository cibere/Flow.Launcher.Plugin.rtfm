from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar

import msgspec

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession

DATA_INDEX_URL = "https://raw.githubusercontent.com/AutoHotkey/AutoHotkeyDocs/refs/heads/v{0}/docs/static/source/data_index.js"
DATA_TOC_URL = "https://raw.githubusercontent.com/AutoHotkey/AutoHotkeyDocs/refs/heads/v{0}/docs/static/source/data_toc.js"
TocTree = list[tuple[str, str] | tuple[str, str, "TocTree"]]

decoder = msgspec.json.Decoder()


class AutoHotkeyDocs(
    PresetLibrary, is_variant=True, favicon_url="https://www.autohotkey.com/favicon.ico"
):
    autohotkey_version: ClassVar[int]

    def __init_subclass__(cls, version: int) -> None:
        cls.autohotkey_version = version
        return super().__init_subclass__(
            base_url=f"https://autohotkey.com/docs/v{version}"
        )

    async def fetch_index(self, session: ClientSession) -> dict[str, str]:
        url = DATA_INDEX_URL.format(self.autohotkey_version)

        async with session.get(url) as res:
            raw_content = await res.content.read()

        content = (
            raw_content.decode().strip().removeprefix("indexData = ").removesuffix(";")
        )

        data: list[tuple[str, str] | tuple[str, str, int]] = decoder.decode(content)

        return {name: self._build_url(str(extra[0]), 0) for name, *extra in data}

    def parse_toc(self, tree: TocTree) -> Iterator[tuple[str, str]]:
        for entry in tree:
            if len(entry) == 2:
                yield entry
            else:
                for key, value in self.parse_toc(entry[2]):
                    yield f"{key} - {entry[0]}", value

    async def fetch_toc(self, session: ClientSession) -> dict[str, str]:
        url = DATA_TOC_URL.format(self.autohotkey_version)

        async with session.get(url) as res:
            raw_content = await res.content.read()

        content = (
            raw_content.decode().strip().removeprefix("tocData = ").removesuffix(";")
        )

        tree: TocTree = decoder.decode(content)

        return {
            name: self._build_url(str(url), 0) for name, url in self.parse_toc(tree)
        }

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        index_cache = await self.fetch_index(session)
        toc_cache = await self.fetch_toc(session)
        self.cache = index_cache | toc_cache


class AutoHotkeyDocsV2(AutoHotkeyDocs, version=2): ...


class AutoHotkeyDocsV1(AutoHotkeyDocs, version=1): ...


preset = (AutoHotkeyDocsV1, AutoHotkeyDocsV2)
