from __future__ import annotations

import asyncio
from yarl import URL
from aiohttp import ClientSession
from .icons import get_icon as _get_icon
from typing import Self, Any
from pathlib import Path

from yarl import URL
from aiohttp import ClientSession
from pathlib import Path

class Library:
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
            f"<{self.__class__.__name__} {self.name=} {self.url=} {self.icon=} {self.use_cache=}>"
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

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        raise NotImplementedError
    
    def _build_url(self, piece: str, port: int) -> str:
        if self.path:
            base_url = URL.build(
                scheme="http", host="localhost", port=port, path="/local-docs"
            )
            url = base_url / self.name / piece
            return str(url)
        elif url := self.url:
            return str(url.joinpath(piece.strip("/")))
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
