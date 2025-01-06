from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from .icons import get_icon as _get_icon
import re
from typing import Self, Any
from pathlib import Path
from .sphinx_object import SphinxObjectFileReader


class SphinxLibrary:
    def __init__(self, name: str, loc: URL | Path, *, use_cache: bool):
        self.name = name
        self.loc = loc
        self.icon: str | None = None
        self.cache: dict[str, str] | None = None
        self.use_cache = use_cache

    @property
    def url(self) -> URL | None:
        return self.loc if isinstance(self.loc, URL) else None

    @property
    def path(self) -> Path | None:
        return self.loc if isinstance(self.loc, Path) else None

    def __repr__(self) -> str:
        return (
            f"<SphinxLibrary {self.name=} {self.url=} {self.icon=} {self.use_cache=}>"
        )

    async def fetch_icon(self) -> str | None:
        if path := self.path:
            loc = path / "index.html"
        else:
            loc = self.loc

        self.icon = await asyncio.to_thread(_get_icon, self.name, loc)
        if self.icon is None:
            self.icon = "assets/app.png"
        return self.icon

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

    def _build_url(self, piece: str, port: int) -> str:
        if self.path:
            base_url = URL.build(
                scheme="http", host="localhost", port=port, path="/local-docs"
            )
            url = base_url / self.name / piece
            return str(url)
        elif url := self.url:
            return str(url.joinpath(piece))
        else:
            raise ValueError(
                f"Expected location to be of type URL or Path, not {self.loc.__class__.__name__!r}"
            )

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        kwargs = {"name": data["name"], "use_cache": data["use_cache"]}

        loc: str = data["loc"]

        if loc.startswith(("http://", "https://")):
            kwargs["loc"] = URL(loc)
        elif loc.startswith("file:///"):
            kwargs["loc"] = Path(URL(loc).path.strip("/"))
        else:
            kwargs["loc"] = Path(loc)

        return cls(**kwargs)
