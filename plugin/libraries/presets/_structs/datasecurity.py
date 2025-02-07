from __future__ import annotations

import msgspec


class HeaderEntry(msgspec.Struct):
    level: int
    title: str
    slug: str
    link: str
    children: list[HeaderEntry]


class Response(msgspec.Struct):
    key: str
    path: str
    title: str
    lang: str
    headers: list[HeaderEntry]
