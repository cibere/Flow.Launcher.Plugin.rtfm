from __future__ import annotations

import msgspec


class DocEntry(msgspec.Struct):
    location: str
    text: str
    title: str


class SearchIndexFile(msgspec.Struct):
    config: dict
    docs: list[DocEntry]
