from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from ..icons import get_icon as _get_icon
import re
from typing import Self, Any, ClassVar
from pathlib import Path

import io
import zlib, json
from typing import Generator
from yarl import URL
from aiohttp import ClientSession
from pathlib import Path
from ..library import Library

class AutoHotkeyDocs(Library):
    autohotkey_version: ClassVar[int]
    inventory_url: ClassVar[str]

    def __init__(self, name: str, *, use_cache: bool):
        super().__init__(name, URL(f"https://autohotkey.com/docs/v{self.autohotkey_version}"), use_cache=use_cache)

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.inventory_url) as res:
            raw_content = await res.content.read()

        content = raw_content.decode().strip().removeprefix("indexData = ").removesuffix(";")

        data: list[tuple[str, str] | tuple[str, str, int]] = json.loads(content)

        self.cache = {
            name:self._build_url(str(extra[0]), webserver_port) for name, *extra in data
        }

class AutoHotkeyDocsV2(AutoHotkeyDocs):
    inventory_url: ClassVar[str] = "https://raw.githubusercontent.com/AutoHotkey/AutoHotkeyDocs/refs/heads/v2/docs/static/source/data_index.js"
    autohotkey_version: ClassVar[int] = 2

class AutoHotkeyDocsV1(AutoHotkeyDocs):
    inventory_url: ClassVar[str] = "https://raw.githubusercontent.com/AutoHotkey/AutoHotkeyDocs/refs/heads/v1/docs/static/source/data_index.js"
    autohotkey_version: ClassVar[int] = 1