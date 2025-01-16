from __future__ import annotations

import msgspec


class SearchHighlights(msgspec.Struct):
    title: list[str]
    content: list[str]
    content_explicit: list[str]


class SearchHit(msgspec.Struct):
    id: str
    url: str
    title: str
    breadcrumbs: str
    highlights: SearchHighlights


class SearchResponse(msgspec.Struct):
    hits: list[SearchHit]


class ErrorResponse(msgspec.Struct):
    error: str
    key: str
