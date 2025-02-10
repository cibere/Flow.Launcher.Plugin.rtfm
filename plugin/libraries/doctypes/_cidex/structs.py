from collections.abc import Mapping
from typing import Any

from msgspec import Struct

from ...entry import Entry


class BaseIndex(Struct):
    name: str
    favicon_url: str | None


class ApiIndex(BaseIndex, tag="api-index"):
    url: str
    api_type: str
    headers: dict[str, str]
    options: dict[str, Any]
    version: str = "2.0"


class CacheIndex(BaseIndex, tag="cache-index"):
    cache: Mapping[str, str | Entry]
    version: str = "2.0"


class VariantManifest(Struct, tag="variant-manifest"):
    variants: list[str]
    version: str = "2.0"
