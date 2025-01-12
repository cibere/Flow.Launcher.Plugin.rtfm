from typing import Literal

from ...libraries.library import PartialLibrary
from .base import Payload


class PluginSettings(Payload):
    port: int
    keyword: str
    libraries: list[PartialLibrary]


class ExportSettingsResponse(Payload):
    data: str
    success: Literal[True] = True


class ImportSettingsRequest(Payload):
    data: str
