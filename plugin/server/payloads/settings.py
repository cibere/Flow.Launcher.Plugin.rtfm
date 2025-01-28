from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Literal

from ...libraries.library import PartialLibrary
from .base import Payload

if TYPE_CHECKING:
    from ...plugin import RtfmPlugin


class PluginSettings(Payload):
    port: int
    keyword: str
    libraries: list[PartialLibrary]
    debug: bool = False

    @classmethod
    def parse_form_data(cls, data: dict[str, str]) -> PluginSettings:
        kwargs: dict[str, Any] = {}
        raw_docs: dict[int, dict[str, Any]] = defaultdict(lambda: {})

        for key, value in data.items():
            parts = key.split(".")
            match parts[0]:
                case "plugin":
                    match parts[1]:
                        case "port":
                            kwargs["port"] = int(value)
                        case "keyword":
                            kwargs["keyword"] = value or "*"
                        case "debug":
                            kwargs["debug"] = True
                case "doc":
                    idx = int(parts[1])
                    match parts[2]:
                        case "use_cache":
                            value = True
                        case "keyword":
                            parts[2] = "name"
                            if not value:
                                value = "*"

                    raw_docs[idx][parts[2]] = value

        kwargs["libraries"] = [PartialLibrary(**opts) for opts in raw_docs.values()]
        return cls(**kwargs)

    async def save(self, plugin: RtfmPlugin) -> None:
        plugin.static_port = self.port
        plugin.main_kw = self.keyword
        plugin.debug_mode = self.debug

        await plugin.update_libraries(self.libraries)
        asyncio.create_task(plugin.build_rtfm_lookup_tables())

    @classmethod
    def from_plugin(cls, plugin: RtfmPlugin) -> PluginSettings:
        return cls(
            port=plugin.static_port,
            keyword=plugin.main_kw,
            debug=plugin.debug_mode,
            libraries=[lib.to_partial() for lib in plugin.libraries.values()],
        )


class ExportSettingsResponse(Payload):
    data: str
    success: Literal[True] = True


class ImportSettingsRequest(Payload):
    data: str
