from typing import Literal

from rtfm_lookup import PartialManual

from .base import Payload


class GetManualPayload(Payload):
    url: str
    name: str


class GetManualResponse(Payload):
    data: PartialManual
    success: Literal[True] = True
