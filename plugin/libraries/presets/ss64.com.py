from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

import bs4

from plugin.libraries.entry import Entry
from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class SS64Parser:
    soup: bs4.BeautifulSoup

    def __init__(
        self,
        data: bytes,
        url_builder: Callable[[str], str],
        *,
        is_powershell: bool = False,
    ) -> None:
        self.data = data
        self.cache: dict[str, str | Entry] = {}
        self.url_builder = url_builder
        self.is_powershell = is_powershell

    def parse(self) -> dict[str, str | Entry]:
        self.soup = bs4.BeautifulSoup(self.data, "html.parser")

        container = self.soup.find_all("table")[-1]
        assert isinstance(container, bs4.Tag)

        rows = container.find_all("tr")
        for row in rows:
            if not isinstance(row, bs4.Tag):
                continue

            tds = row.find_all("td")
            if not tds:
                continue

            tds0 = tds[0]
            if not isinstance(tds0, bs4.Tag) or tds0.attrs.get("class") == "ix":
                continue

            cmd_name_td = tds[1]
            if not isinstance(cmd_name_td, bs4.Tag):
                continue

            atag = cmd_name_td.find("a")
            if isinstance(atag, bs4.Tag):
                command_name = atag.text.strip()
                path = str(atag.attrs.get("href", "")).strip()
            else:
                command_name = cmd_name_td.text.strip()
                path = ""

            aliases = []
            if self.is_powershell:
                raw_aliases = tds[2].text.strip().replace(" ", "")
                if raw_aliases:
                    aliases = raw_aliases.split("/")

            short_description = tds[-1].text
            url = self.url_builder(path)

            if command_name:
                name = f"{command_name}"
                self.cache[name] = Entry(name, url, {"sub": short_description})
                alias_sub_prefix = f"Alias of: {name} | "
            else:
                alias_sub_prefix = ""

            for alias in aliases:
                self.cache[alias] = Entry(
                    alias, url, {"sub": f"{alias_sub_prefix}{short_description}"}
                )

        return self.cache


class SS64Base(PresetLibrary, is_variant=True, favicon_url="https://ss64.com"):
    ss64_version: ClassVar[str]

    def __init_subclass__(cls, version: str) -> None:
        cls.ss64_version = version
        return super().__init_subclass__(
            base_url=f"https://ss64.com/{version}",
        )

    async def fetch_icon(self) -> str | None:
        return await super().fetch_icon()

    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        async with session.get(self.url) as res:
            raw_content: bytes = await res.content.read()

        parser = SS64Parser(
            raw_content,
            partial(self._build_url, port=webserver_port),
            is_powershell=self.ss64_version == "ps",
        )

        self.cache = await asyncio.to_thread(parser.parse)


class SS64Mac(SS64Base, version="mac"): ...


class SS64Bash(SS64Base, version="bash"): ...


class SS64NT(SS64Base, version="nt"): ...


class SS64PS(SS64Base, version="ps"): ...


preset = (SS64Bash, SS64Mac, SS64PS, SS64NT)
