from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Self

from yarl import URL

from .icons import get_icon as _get_icon

if TYPE_CHECKING:
    from aiohttp import ClientSession

BuilderType = Callable[[str, int], str]


class Library:
    classname: ClassVar[str]
    is_preset: ClassVar[bool]

    def __init__(self, name: str, loc: URL | Path, *, use_cache: bool) -> None:
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
        return f"<{self.__class__.__name__} {self.name=} {self.url=} {self.icon=} {self.use_cache=}>"

    async def fetch_icon(self) -> str | None:
        loc = path / "index.html" if (path := self.path) else self.loc

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
        if url := self.url:
            return str(url.joinpath(piece.strip("/")))
        raise ValueError(
            f"Expected location to be of type URL or Path, not {self.loc.__class__.__name__!r}"
        )

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        if data['type'] != cls.classname:
            raise RuntimeError("Invalid Type")
        
        kwargs = {"name": data["name"], "use_cache": data["use_cache"]}

        if data.get("loc") is not None:
            loc: str = data["loc"]

            if loc.startswith(("http://", "https://")):
                kwargs["loc"] = URL(loc)
            elif loc.startswith("file:///"):
                kwargs["loc"] = Path(URL(loc).path.strip("/"))
            else:
                kwargs["loc"] = Path(loc)

        return cls(**kwargs)

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "use_cache": self.use_cache,
            "type": self.classname,
            "loc": None if self.is_preset else str(self.loc),
            "name": self.name,
        }
