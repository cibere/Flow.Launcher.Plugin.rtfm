from __future__ import annotations

import msgspec

from .libraries.library import PartialLibrary  # noqa: TC001


class RtfmBetterSettings(msgspec.Struct):
    main_kw: str = "rtfm"
    static_port: int = 0
    libraries: list[PartialLibrary] = []

    @classmethod
    def decode(cls, data: str) -> RtfmBetterSettings:
        return decoder.decode(data)

    def encode(self) -> bytes:
        return encoder.encode(self)


encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder(RtfmBetterSettings)
