from typing import Self

import msgspec


class RtfmBetterSettings(msgspec.Struct):
    main_kw: str = "rtfm"
    static_port: int = 0

    @classmethod
    def decode(cls, data: str) -> Self:
        return msgspec.json.decode(data, type=cls)

    def encode(self) -> bytes:
        return msgspec.json.encode(self)
