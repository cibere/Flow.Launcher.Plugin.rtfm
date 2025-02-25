from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Any

import msgspec

from rtfm_lookup import IndexerName, PartialManual

if TYPE_CHECKING:
    from .plugin import RtfmPlugin


# region Current


class RtfmBetterSettings(msgspec.Struct, tag="3.0", tag_field="version"):
    main_kw: str = "rtfm"
    static_port: int = 0
    manuals: list[PartialManual] = []
    debug_mode: bool = False
    simple_view: bool = False
    reset_query: bool = False

    @classmethod
    def decode(cls, data: bytes | str) -> RtfmBetterSettings:
        try:
            return v3_decoder.decode(data)
        except msgspec.DecodeError as error:
            try:
                settings = v2_decoder.decode(data)
            except msgspec.DecodeError:
                raise error from None
            return settings.convert()

    def encode(self) -> bytes:
        return encoder.encode(self)

    @classmethod
    def parse_form_data(cls, data: dict[str, str]) -> RtfmBetterSettings:
        kwargs: dict[str, Any] = {}
        raw_docs: dict[str, dict[str, Any]] = defaultdict(lambda: {"options": {"cache_results": False}})

        for raw_key, value in data.items():
            match raw_key.split("."):
                case ["plugin", "port"]:
                    kwargs["static_port"] = int(value)
                case ["plugin", "keyword"]:
                    kwargs["main_kw"] = value or "*"
                case ["plugin", "debug_mode" | "simple_view" | "reset_query" as name]:
                    kwargs[name] = True
                case ["doc", idx, "loc"]:
                    raw_docs[idx]["loc"] = value
                case ["doc", idx, "keyword"]:
                    raw_docs[idx]["name"] = value
                case ["doc", idx, "type"]:
                    raw_docs[idx]["type"] = IndexerName(value)
                case ["doc", idx, "cache_results"]:
                    raw_docs[idx]["options"]["cache_results"] = True
                case ["doc", idx, name]:
                    raw_docs[idx]["options"][name] = value
                case other:
                    raise ValueError(f"Unknown Settings Key: {other!r}")

        kwargs["manuals"] = [PartialManual(**opts) for opts in raw_docs.values()]
        return cls(**kwargs)

    async def save(self, plugin: RtfmPlugin) -> None:
        plugin.better_settings.static_port = self.static_port
        plugin.better_settings.main_kw = self.main_kw
        plugin.better_settings.simple_view = self.simple_view
        plugin.better_settings.reset_query = self.reset_query
        plugin.better_settings.manuals = self.manuals

        if self.debug_mode != plugin.better_settings.debug_mode:
            plugin.logs.update_debug(self.debug_mode)
            plugin.better_settings.debug_mode = self.debug_mode

        plugin.dump_settings()
        plugin.rtfm.load_partials(*self.manuals)
        plugin.rtfm.trigger_cache_reload()
        asyncio.create_task(plugin.ensure_keywords())


# region Legacy


class PartialLibrary(msgspec.Struct):
    name: str
    type: str
    loc: str
    cache_results: bool = False
    is_api: bool = False


class RtfmBetterSettingsV2(msgspec.Struct):
    main_kw: str = "rtfm"
    static_port: int = 0
    libraries: list[PartialLibrary] = []
    version: str | None = None
    debug_mode: bool = False
    simple_view: bool = False
    reset_query: bool = False

    def convert(self) -> RtfmBetterSettings:
        return RtfmBetterSettings(
            main_kw=self.main_kw,
            static_port=self.static_port,
            debug_mode=self.debug_mode,
            simple_view=self.simple_view,
            reset_query=self.reset_query,
            manuals=[
                PartialManual(
                    name=lib.name,
                    type=IndexerName(
                        {
                            "Preset": "cibere-rtfm-indexes",
                            "Gidocgen": "gidocgen",
                            "Intersphinx": "intersphinx",
                            "Mkdocs": "mkdocs",
                        }[lib.type]
                    ),
                    loc=lib.loc,
                    options={
                        "cache_results": lib.cache_results,
                    },
                )
                for lib in self.libraries
            ],
        )


# region json

encoder = msgspec.json.Encoder()
v3_decoder = msgspec.json.Decoder(RtfmBetterSettings)
v2_decoder = msgspec.json.Decoder(RtfmBetterSettingsV2)
