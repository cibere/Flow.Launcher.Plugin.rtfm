from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec

from .preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession

json = msgspec.json.Decoder()


class RtfmIndexBase(PresetLibrary):
    index_name: ClassVar[str]

    def __init_subclass__(
        cls,
        name: str,
        url: str,
        favicon_url: str | None = None,
        is_variant: bool = False,
    ) -> None:
        cls.index_name = name
        super().__init_subclass__(
            base_url=url, favicon_url=favicon_url or url, is_variant=is_variant
        )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(
            f"https://rtfm-indexes.cibere.dev/indexes/{self.index_name}.json"
        ) as res:
            raw_content: bytes = await res.content.read()

        with open("data", "wb") as f:
            f.write(raw_content)

        self.cache = json.decode(raw_content)
