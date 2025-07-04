from typing import Literal

from .base import Payload


class ErrorResponse(Payload):
    message: str
    success: Literal[False] = False
