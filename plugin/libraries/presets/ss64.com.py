from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

import bs4

from plugin.libraries.preset import PresetLibrary

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


class SS64Base(PresetLibrary):
    ss64_version: ClassVar[str]

    def __init_subclass__(cls, version: str) -> None:
        cls.ss64_version = version
        return super().__init_subclass__(
            base_url=f"https://ss64.com/{version}", favicon_url="https://ss64.com"
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


presets = (SS64Bash, SS64Mac, SS64PS, SS64NT)
