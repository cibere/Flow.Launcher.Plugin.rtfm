from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from .icons import get_icon as _get_icon
import re
from pathlib import Path
from .sphinx_object import SphinxObjectFileReader


class SphinxLibrary:
    def __init__(self, name: str, url: str | URL, *, session: ClientSession):
        self.name = name
        self.url = url if isinstance(url, URL) else URL(url)
        self.session = session
        self.icon: str | None = None
        self.file: SphinxObjectFileReader | None = None
        self.cache: dict[str, str] | None = None

    @property
    def is_local(self) -> bool:
        return self.url.scheme == "file"

    def __repr__(self) -> str:
        return f"<SphinxLibrary {self.name=} {self.url=} {self.icon=}>"

    async def fetch_icon(self) -> str | None:
        if self.url.scheme == "file":
            loc = Path(self.url.path.strip("/")) / "index.html"
        else:
            loc = self.url

        self.icon = await asyncio.to_thread(_get_icon, self.name, loc)
        if self.icon is None:
            self.icon = "assets/app.png"
        return self.icon

    async def fetch_file(self) -> SphinxObjectFileReader:
        self.file = await SphinxObjectFileReader.from_url(
            self.url, session=self.session
        )
        return self.file

    async def build_cache(self) -> None:
        file = await self.fetch_file()

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

            cache[f"{prefix}{key}"] = self._build_url(location)

        self.cache = cache

    def _build_url(self, piece: str) -> str:
        if self.is_local:
            base_url = URL.build(
                scheme="http", host="localhost", port=2907, path="/local-docs"
            )
            url = base_url / self.name / piece
            return str(url)
        else:
            return str(self.url.joinpath(piece))
