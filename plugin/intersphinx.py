"""
From https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original intersphinx parsing code
"""

from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from .icons import get_icon as _get_icon
import re
from typing import Self, Any
from pathlib import Path

import io
import zlib
from typing import Generator
from yarl import URL
from aiohttp import ClientSession
from pathlib import Path
from .library import Library
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
        cls: type[SphinxObjectFileReader], url: URL, *, session: ClientSession
    ) -> SphinxObjectFileReader:
        page = url.joinpath("objects.inv")
        async with session.get(page) as resp:
            if resp.status != 200:
                raise ValueError("Could not get objects.inv file")
            return cls(await resp.read())

    @classmethod
    def from_file(
        cls: type[SphinxObjectFileReader], path: Path
    ) -> SphinxObjectFileReader:
        path = path / "objects.inv"
        if not path.exists():
            raise ValueError(f"file does not exist: {path}")
        return cls(path.read_bytes())


class SphinxLibrary(Library):
    async def fetch_file(self, session: ClientSession) -> SphinxObjectFileReader:
        if url := self.url:
            return await SphinxObjectFileReader.from_url(url, session=session)
        elif path := self.path:
            return SphinxObjectFileReader.from_file(path)
        else:
            raise ValueError(
                f"Expected location to be of type URL or Path, not {self.loc.__class__.__name__!r}"
            )

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        file = await self.fetch_file(session)

        # key: URL
        cache: dict[str, str] = {}

        # first line is version info
        inv_version = file.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = file.readline().rstrip()[11:]
        version = file.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = file.readline()
        if "zlib" not in line:
            raise RuntimeError(
                f"Invalid objects.inv file, not z-lib compatible. Line: {line}"
            )

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in file.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in cache:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            cache[f"{prefix}{key}"] = self._build_url(location, webserver_port)

        self.cache = cache