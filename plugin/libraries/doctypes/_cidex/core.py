from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession
from flogin.utils import print
from yarl import URL

from ...library import Library
from .apis import api_handlers
from .structs import (
    ApiIndex,
    CacheIndex,
    VariantManifest,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession

CidexResponse = CacheIndex | VariantManifest | ApiIndex
msgpack = msgspec.msgpack.Decoder(type=CidexResponse)
INDEX_URL = (
    "https://github.com/cibere/Rtfm-Indexes/raw/refs/heads/master/indexes_v2/{}.cidex"
)


class CidexBase(Library):
    _api_info: ApiIndex

    def _get_url(self) -> URL:
        raise NotImplementedError

    def _resolve_variant_via_exact_match(
        self, url: URL, variants: list[str]
    ) -> str | None:
        choice = None
        print(f"Attempting to resolve varint for {url!r}")

        for variant in variants:
            if variant in url.path:
                if choice is not None:
                    return print("Returning as duplicate")
                choice = variant
                print(f"Setting choice to {variant}")
        print(f"{choice=}")
        return choice

    def resolve_variant(self, manifest: VariantManifest) -> str | None:
        if not self.url:
            return

        return self._resolve_variant_via_exact_match(self.url, manifest.variants)

    async def fetch_index(
        self, session: ClientSession, url: URL
    ) -> CacheIndex | ApiIndex:
        async with session.get(url) as res:
            raw_content: bytes = await res.content.read()

        data: CidexResponse = msgpack.decode(raw_content)

        if isinstance(data, VariantManifest):
            variant = self.resolve_variant(data)
            if not variant:
                raise ValueError("Unable to resolve correct variant")

            parts = list(url.parts)
            parts[-1] = parts[-1].replace(".cidex", f"-{variant}.cidex")
            new_url = url.with_path("/".join(parts))

            assert new_url != url
            print(f"{new_url=}")
            return await self.fetch_index(session, new_url)

        return data

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self._get_url()

        index = await self.fetch_index(session, url)

        if isinstance(index, ApiIndex):
            self.is_api = True
            self._api_info = index
        else:
            self.cache = index.cache

        self.favicon_url = index.favicon_url

    async def make_request(self, session: ClientSession, query: str) -> None:
        info = self._api_info
        handler = api_handlers[info.api_type]

        self.cache = await handler(query, info, session)


class PresetDoctype(CidexBase):
    typename: ClassVar[str] = "Preset"

    def _get_url(self) -> URL:
        url = self.url
        if url is None:
            raise ValueError("Local presets are not supported")

        index_url = INDEX_URL.format(str(url.host).removeprefix("www."))
        print(f"{index_url=}")
        return URL(index_url)


class CidexDoctype(CidexBase):
    typename: ClassVar[str] = "cidex"

    def _get_url(self) -> URL:
        url = self.url
        if url is None:
            raise ValueError("Local cidex docs are not supported")
        return url / "index.cidex"


doctype = PresetDoctype, CidexDoctype
