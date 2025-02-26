from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any

import msgspec
from rtfm_lookup import IndexerName, PartialManual

if TYPE_CHECKING:
    from .plugin import RtfmPlugin

log = logging.getLogger(__name__)

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
        raw = dict_decoder.decode(data)
        version = raw.get("version", None)
        if version == "3.0":
            return current_decoder.decode(data)

        log.debug(
            "Settings version not current, running legacy decoders. Version: %r",
            version,
        )
        for decoder in legacy_decoders:
            try:
                settings = decoder.decode(data)
            except msgspec.DecodeError as e:
                log.debug("Given settings does not fit %r", decoder.type, exc_info=e)
                continue

            return settings.convert()

        log.error("Failed to decode settings. Raw Data: %r\nSerialized: %r", data, raw)
        raise ValueError("Could not match data to a decoder")

    def encode(self) -> bytes:
        return encoder.encode(self)

    @classmethod
    def parse_form_data(cls, data: dict[str, str]) -> RtfmBetterSettings:
        kwargs: dict[str, Any] = {}
        raw_docs: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"options": {"dont_cache_results": True}}
        )

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
                case ["doc", idx, "dont_cache_results"]:
                    raw_docs[idx]["options"]["dont_cache_results"] = False
                case ["doc", idx, name]:
                    raw_docs[idx]["options"][name] = value
                case other:
                    raise ValueError(f"Unknown Settings Key: {other!r}")

        kwargs["manuals"] = [PartialManual(**opts) for opts in raw_docs.values()]
        return cls(**kwargs)

    async def save(self, plugin: RtfmPlugin) -> None:
        log.debug(
            "Saving static port. %r -> %r",
            plugin.better_settings.static_port,
            self.static_port,
        )
        plugin.better_settings.static_port = self.static_port

        log.debug(
            "Saving main kw. %r -> %r", plugin.better_settings.main_kw, self.main_kw
        )
        plugin.better_settings.main_kw = self.main_kw

        log.debug(
            "Saving simple_view. %r -> %r",
            plugin.better_settings.simple_view,
            self.simple_view,
        )
        plugin.better_settings.simple_view = self.simple_view

        log.debug(
            "Saving reset_query. %r -> %r",
            plugin.better_settings.reset_query,
            self.reset_query,
        )
        plugin.better_settings.reset_query = self.reset_query

        log.debug(
            "Saving manuals. %r -> %r", plugin.better_settings.manuals, self.manuals
        )
        plugin.better_settings.manuals = self.manuals

        if self.debug_mode != plugin.better_settings.debug_mode:
            log.debug(
                "Saving debug mode. %r -> %r",
                plugin.better_settings.debug_mode,
                self.debug_mode,
            )
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
    use_cache: bool = False
    is_api: bool = False


class LegacySettingsV2(msgspec.Struct):
    main_kw: str
    static_port: int
    libraries: list[PartialLibrary]
    debug_mode: bool
    simple_view: bool

    def convert(self) -> RtfmBetterSettings:
        return RtfmBetterSettings(
            main_kw=self.main_kw,
            static_port=self.static_port,
            debug_mode=self.debug_mode,
            simple_view=self.simple_view,
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
                        "dont_cache_results": not lib.use_cache,
                    },
                )
                for lib in self.libraries
            ],
        )


class LegacySettingsV1(msgspec.Struct):
    keyword: str
    port: int
    libraries: list[PartialLibrary]
    debug: bool
    simple: bool

    def convert(self) -> RtfmBetterSettings:
        return RtfmBetterSettings(
            main_kw=self.keyword,
            static_port=self.port,
            debug_mode=self.debug,
            simple_view=self.simple,
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
                        "dont_cache_results": not lib.use_cache,
                    },
                )
                for lib in self.libraries
            ],
        )


# region json

encoder = msgspec.json.Encoder()
current_decoder = msgspec.json.Decoder(RtfmBetterSettings)
dict_decoder = msgspec.json.Decoder(type=dict)
legacy_decoders = (
    msgspec.json.Decoder(type=LegacySettingsV1),
    msgspec.json.Decoder(type=LegacySettingsV2),
)
