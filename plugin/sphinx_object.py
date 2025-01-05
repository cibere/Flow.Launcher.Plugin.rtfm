"""
From https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import io
import zlib
from typing import Generator
from yarl import URL
from aiohttp import ClientSession
from pathlib import Path


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer: bytes):
        self.stream = io.BytesIO(buffer)

    def readline(self) -> str:
        return self.stream.readline().decode("utf-8")

    def skipline(self) -> None:
        self.stream.readline()

    def read_compressed_chunks(self) -> Generator[bytes, None, None]:
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self) -> Generator[str, None, None]:
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")

    @classmethod
    async def from_url(
        cls: type[SphinxObjectFileReader], url: str | URL, *, session: ClientSession
    ) -> SphinxObjectFileReader:
        if isinstance(url, str):
            url = URL(url)

        if url.scheme in ("http", "https"):
            page = url.joinpath("objects.inv")
            async with session.get(page) as resp:
                if resp.status != 200:
                    raise ValueError("Could not get objects.inv file")
                return cls(await resp.read())
        elif url.scheme == "file":
            path = Path(url.path.strip("/")).joinpath("objects.inv")
            if not path.exists():
                raise ValueError(f"file does not exist: {path}")
            return cls(path.read_bytes())
        else:
            raise ValueError("Invalid URL")
