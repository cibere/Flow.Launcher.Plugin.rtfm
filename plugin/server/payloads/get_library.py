from typing import Any, Literal

from msgspec import field

from ...libraries.library import PartialLibrary
from .base import Payload


class GetLibraryPayload(Payload):
    url: str
    name: str
    options: dict[str, Any] = field(default_factory=dict)


class GetLibraryResponse(Payload):
    data: PartialLibrary
    success: Literal[True] = True


class GetLibraryPromptResponse(Payload):
    prompt: str
    options: list[str]
    slug: str
    success: Literal[True] = True
