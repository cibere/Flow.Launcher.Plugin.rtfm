from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal

from ...libraries.library import PartialLibrary
from .base import Payload


class PluginSettings(Payload):
    port: int
    keyword: str
    libraries: list[PartialLibrary]

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
                            kwargs["keyword"] = value
                case "doc":
                    idx = int(parts[1])
                    match parts[2]:
                        case "use_cache":
                            value = True
                        case "keyword":
                            parts[2] = "name"
                    raw_docs[idx][parts[2]] = value

        kwargs["libraries"] = [PartialLibrary(**opts) for opts in raw_docs.values()]
        return cls(**kwargs)


class ExportSettingsResponse(Payload):
    data: str
    success: Literal[True] = True


class ImportSettingsRequest(Payload):
    data: str
