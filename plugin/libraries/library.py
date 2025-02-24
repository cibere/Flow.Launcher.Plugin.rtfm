from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Self

import msgspec
from yarl import URL

from ..icons import get_icon as _get_icon

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from aiohttp import ClientSession
    from flogin import Result

    from .entry import Entry

BuilderType = Callable[[str, int], str]


class PartialLibrary(msgspec.Struct):
    name: str
    type: str
    loc: str
    options: dict[str, Any] = {}

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "loc": self.loc,
            "options": self.options,
        }

    def encode(self) -> bytes:
        return encoder.encode(self)

    @classmethod
    def decode(cls, data: bytes) -> PartialLibrary:
        return decoder.decode(data)


encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder(type=PartialLibrary)


class Library:
    typename: ClassVar[str]
    favicon_url: ClassVar[str] | None = None
    is_api: bool = False
    cache: Mapping[str, Entry | str] | None
    supports_local: ClassVar[bool] = False
    result_cache: dict[str, Iterable[Result]]
    _options: dict[str, Any]

    def __init__(self, name: str, loc: URL | Path, **options: Any) -> None:
        self.name = name
        self.loc = loc
        self.icon: str | None = None
        self.cache = None
        self.result_cache = {}
        self._options = options
        self._options["is_api"] = self.is_api

        if "cache_results" not in options:
            options["cache_results"] = True

    @property
    def variant_name(self) -> str | None:
        return self._options.get("variant")

    @property
    def cache_results(self) -> bool:
        return self._options["cache_results"]

    @property
    def url(self) -> URL | None:
        return self.loc if isinstance(self.loc, URL) else None

    @property
    def path(self) -> Path | None:
        return self.loc if isinstance(self.loc, Path) else None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name=} {self.url=} {self.icon=} {self.cache_results=} {self.typename=} {self.is_api=}>"

    async def fetch_icon(self) -> str | None:
        if self.favicon_url is None:
            loc = path / "index.html" if (path := self.path) else self.loc
        else:
            loc = URL(self.favicon_url)

        self.icon = await asyncio.to_thread(_get_icon, self.name, loc)
        if self.icon is None:
            self.icon = "assets/app.png"
        return self.icon

    async def make_request(self, session: ClientSession, query: str) -> None:
        raise NotImplementedError

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
    def from_partial(cls: type[Self], data: PartialLibrary) -> Self:
        kwargs: dict[str, Any] = {"name": data.name}

        loc: str = data.loc

        if loc.startswith(("http://", "https://")):
            kwargs["loc"] = URL(loc)
        else:
            if not cls.supports_local:
                raise RuntimeError(
                    f"{cls.__name__} does not support local docs. {loc!r} seems to be a local path."
                )
            kwargs["loc"] = Path(loc)

        self = cls(**kwargs)
        self._options = data.options
        return self

    def to_partial(self) -> PartialLibrary:
        return PartialLibrary(
            self.name, type=self.typename, loc=str(self.loc), options=self._options
        )
