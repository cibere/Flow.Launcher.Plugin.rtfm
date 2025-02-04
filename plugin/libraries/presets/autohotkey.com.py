from __future__ import annotations

import json
from typing import TYPE_CHECKING, ClassVar

from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class AutoHotkeyDocs(
    PresetLibrary, is_variant=True, favicon_url="https://www.autohotkey.com/favicon.ico"
):
    autohotkey_version: ClassVar[int]
    inventory_url: ClassVar[str]

    def __init_subclass__(cls, version: int) -> None:
        cls.inventory_url = f"https://raw.githubusercontent.com/AutoHotkey/AutoHotkeyDocs/refs/heads/v{version}/docs/static/source/data_index.js"
        return super().__init_subclass__(
            base_url=f"https://autohotkey.com/docs/v{version}"
        )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.inventory_url) as res:
            raw_content = await res.content.read()

        content = (
            raw_content.decode().strip().removeprefix("indexData = ").removesuffix(";")
        )

        data: list[tuple[str, str] | tuple[str, str, int]] = json.loads(content)

        self.cache = {
            name: self._build_url(str(extra[0]), webserver_port)
            for name, *extra in data
        }


class AutoHotkeyDocsV2(AutoHotkeyDocs, version=2): ...


class AutoHotkeyDocsV1(AutoHotkeyDocs, version=1): ...


preset = (AutoHotkeyDocsV1, AutoHotkeyDocsV2)
