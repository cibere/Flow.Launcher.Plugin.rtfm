from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

import bs4
from yarl import URL

from ..library import Library

if TYPE_CHECKING:
    from aiohttp import ClientSession


class SS64Parser:
    def __init__(
        self,
        data: bytes,
        url_builder: Callable[[str], str],
        *,
        is_powershell: bool = False,
    ) -> None:
        self.data = data
        self.soup = bs4.BeautifulSoup(data, "html.parser")
        self.cache: dict[str, str] = {}
        self.url_builder = url_builder
        self.is_powershell = is_powershell

    def parse(self) -> dict[str, str]:
        container: bs4.Tag = self.soup.find_all("table")[-1]
        rows: list[bs4.Tag] = container.find_all("tr")
        for row in rows:
            tds: list[bs4.Tag] = row.find_all("td")
            if not tds:
                continue
            if tds[0].attrs.get("class") == "ix":
                continue

            cmd_name_td = tds[1]
            atag = cmd_name_td.find("a")
            if isinstance(atag, bs4.Tag):
                command_name = atag.text.strip()
                path = atag.attrs.get("href", "").strip()
            else:
                command_name = cmd_name_td.text.strip()
                path = ""

            aliases = []
            if self.is_powershell:
                raw_aliases = tds[2].text.strip().replace(" ", "")
                if raw_aliases:
                    aliases = raw_aliases.split("/")

            if command_name:
                short_description = tds[-1].text
                url = self.url_builder(path)
                name = f"{command_name} - {short_description}"
                self.cache[name] = url
                for alias in aliases:
                    self.cache[f"{alias} - {name}"] = url

        return self.cache


class SS64Base(Library):
    classname: ClassVar[str]
    ss64_version: ClassVar[str]
    is_preset: ClassVar[bool] = True
    favicon_url: ClassVar[str] | None = "https://ss64.com"

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(
            name,
            URL(f"https://ss64.com/{self.ss64_version}"),
            use_cache=use_cache,
        )

    async def fetch_icon(self) -> str | None:
        return await super().fetch_icon()

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        url = self.url
        if url is None:
            raise ValueError("Local ss64 manuals are not supported")

        async with session.get(url) as res:
            raw_content: bytes = await res.content.read()

        parser = SS64Parser(
            raw_content,
            partial(self._build_url, port=webserver_port),
            is_powershell=self.ss64_version == "ps",
        )

        self.cache = await asyncio.to_thread(parser.parse)


class SS64Mac(SS64Base):
    classname: ClassVar[str] = "SS64 Mac"
    ss64_version: ClassVar[str] = "mac"


class SS64Bash(SS64Base):
    classname: ClassVar[str] = "SS64 Linux"
    ss64_version: ClassVar[str] = "bash"


class SS64NT(SS64Base):
    classname: ClassVar[str] = "SS64 CMD"
    ss64_version: ClassVar[str] = "nt"


class SS64PS(SS64Base):
    classname: ClassVar[str] = "SS64 PowerShell"
    ss64_version: ClassVar[str] = "ps"
