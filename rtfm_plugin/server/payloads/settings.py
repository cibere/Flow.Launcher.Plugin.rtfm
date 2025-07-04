from __future__ import annotations

from typing import Literal

from .base import Payload


class ExportSettingsResponse(Payload):
    data: str
    success: Literal[True] = True


class ImportSettingsRequest(Payload):
    data: str
