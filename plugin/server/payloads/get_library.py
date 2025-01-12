from typing import Literal

from ...libraries.library import PartialLibrary
from .base import Payload


class GetLibraryPayload(Payload):
    url: str
    name: str


class GetLibraryResponse(Payload):
    data: PartialLibrary
    success: Literal[True] = True
