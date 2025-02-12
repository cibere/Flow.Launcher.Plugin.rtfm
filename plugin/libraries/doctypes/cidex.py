from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import msgspec
from aiohttp import ClientSession
from yarl import URL

from plugin.libraries.doctypes._structs.cidex import (
    ApiIndex,
    Cache,
    CacheIndex,
    VariantManifest,
)
from plugin.libraries.library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession

CidexResponse = CacheIndex | VariantManifest | ApiIndex
msgpack = msgspec.msgpack.Decoder(type=CidexResponse)
api_decoder = msgspec.json.Decoder(type=Cache)
INDEX_URL = "https://github.com/cibere/Rtfm-Indexes/raw/refs/heads/indexes-v2/indexes_v2/{}.cidex"


class CidexBase(Library):
    _api_info: ApiIndex

    def _get_url(self) -> URL:
        raise NotImplementedError

    def _resolve_variant_via_exact_match(
        self, url: URL, variants: list[str]
    ) -> str | None:
        choice = None

        for variant in variants:
            if variant in url.path:
                if choice is not None:
                    return
                choice = variant
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
            return await self.fetch_index(session, new_url)

        return data

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self._get_url()

        index = await self.fetch_index(session, url)

        if isinstance(index, ApiIndex):
            self.is_api = True
            self._api_info = index
            self.cache = {}
        else:
            self.cache = index.cache

        self.favicon_url = index.favicon_url

    async def make_request(self, session: ClientSession, query: str) -> None:
        info = self._api_info

        payload = {"query": query, "options": info.options}
        async with session.post(info.url, json=payload) as res:
            raw_content = await res.read()

        self.cache = api_decoder.decode(raw_content)


class PresetDoctype(CidexBase):
    typename: ClassVar[str] = "Preset"

    def _get_url(self) -> URL:
        url = self.url
        if url is None:
            raise ValueError("Local presets are not supported")

        index_url = INDEX_URL.format(str(url.host).removeprefix("www."))
        return URL(index_url)


class CidexDoctype(CidexBase):
    typename: ClassVar[str] = "cidex"

    def _get_url(self) -> URL:
        url = self.url
        if url is None:
            raise ValueError("Local cidex docs are not supported")
        return url.with_path("index.cidex")


doctype = PresetDoctype, CidexDoctype
