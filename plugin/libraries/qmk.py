from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from ..icons import get_icon as _get_icon
import re
from typing import Self, Any, ClassVar, TypedDict
from pathlib import Path

import io
import zlib
from typing import NotRequired
from yarl import URL
from aiohttp import ClientSession
from pathlib import Path
from ..library import Library
import msgspec
from msgspec import json

class QmkInvEntry(msgspec.Struct):
    text: str
    items: list[QmkInvEntry] | None = None
    link: str | None = None

    def parse_self(self, webserver_port: int, builder) -> dict[str, str]:
        cache: dict[str, str] = {}

        if self.items is not None:
            for entry in self.items:
                cache.update(entry.parse_self(webserver_port, builder))
        if self.link is not None:
            cache[self.text] = builder(self.link, webserver_port)
        return cache

class QmkDocs(Library):
    inventory_url: ClassVar[str] = "https://raw.githubusercontent.com/qmk/qmk_firmware/refs/heads/master/docs/_sidebar.json"

    def __init__(self, name: str, *, use_cache: bool):
        super().__init__(name, URL(f"https://docs.qmk.fm/"), use_cache=use_cache)

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.inventory_url) as res:
            raw_content: bytes = await res.content.read()
        
        data = json.decode(raw_content, type=list[QmkInvEntry])

        cache = {}

        for entry in data:
            cache.update(entry.parse_self(webserver_port, self._build_url))
        self.cache = cache