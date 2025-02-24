from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Any

import msgspec

from .libraries.library import PartialLibrary

if TYPE_CHECKING:
    from .plugin import RtfmPlugin


def _defaultdict_factory():
    return defaultdict(_defaultdict_factory)


class RtfmBetterSettings(msgspec.Struct):
    main_kw: str = "rtfm"
    static_port: int = 0
    libraries: list[PartialLibrary] = []
    version: str | None = (
        None  # For backwards compatible settings in the future. Incase the format changes again, this key can be used to determine which format to parse.
    )
    debug_mode: bool = False
    simple_view: bool = False
    reset_query: bool = False

    @classmethod
    def decode(cls, data: bytes | str) -> RtfmBetterSettings:
        return decoder.decode(data)

    def encode(self) -> bytes:
        return encoder.encode(self)

    @classmethod
    def parse_form_data(cls, data: dict[str, str]) -> RtfmBetterSettings:
        kwargs: dict[str, Any] = {}
        raw_docs: dict[int, dict[str, Any]] = _defaultdict_factory()

        for key, value in data.items():
            parts = key.split(".")
            match parts[0]:
                case "plugin":
                    name = parts[1]

                    if name == "port":
                        kwargs["static_port"] = int(value)
                    elif name == "keyword":
                        kwargs["main_kw"] = value or "*"
                    elif name in ("debug_mode", "simple_view", "reset_query"):
                        kwargs[name] = True
                    else:
                        raise ValueError(f"Unknown Settings Key: {key!r}")
                case "doc":
                    idx = int(parts[1])

                    match parts[2]:
                        case "cache_results":
                            raw_docs[idx]["options"]["cache_results"] = True
                            continue
                        case "keyword":
                            parts[2] = "name"
                            if not value:
                                value = "*"

                    raw_docs[idx][parts[2]] = value

        kwargs["libraries"] = [PartialLibrary(**opts) for opts in raw_docs.values()]
        return cls(**kwargs)

    async def save(self, plugin: RtfmPlugin) -> None:
        plugin.better_settings.static_port = self.static_port
        plugin.better_settings.main_kw = self.main_kw
        plugin.better_settings.simple_view = self.simple_view
        plugin.better_settings.reset_query = self.reset_query

        if self.debug_mode != plugin.better_settings.debug_mode:
            plugin.logs.update_debug(self.debug_mode)
            plugin.better_settings.debug_mode = self.debug_mode

        plugin.dump_settings()
        await plugin.update_libraries(self.libraries)
        asyncio.create_task(plugin.build_rtfm_lookup_tables())


encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder(RtfmBetterSettings)
