from typing import Self

import msgspec

encoder = msgspec.json.Encoder()
decoders = {}


class Payload(msgspec.Struct):
    def encode(self) -> bytes:
        return encoder.encode(self)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoder = decoders.get(cls)
        if not decoder:
            decoder = msgspec.json.Decoder(type=cls)
            decoders[cls] = decoder
        return decoder.decode(data)
