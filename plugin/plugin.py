"""
Adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re

import aiohttp
import yarl
from flogin import Plugin, QueryResponse, Settings
from flogin.utils import cached_property

from .icons import get_icon
from .results import OpenSettingsResult, ReloadCacheResult
from .server.core import run_app as start_webserver
from .settings import RtfmSettings
from .sphinx_object import SphinxObjectFileReader

log = logging.getLogger("rtfm")


class RtfmPlugin(Plugin[RtfmSettings]):
    _rtfm_cache: dict[str, dict[str, str]]
    session: aiohttp.ClientSession
    icons: dict[str, str]

    def __init__(self) -> None:
        super().__init__(settings_no_update=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.on_context_menu)
        self.register_event(self.init, "on_initialization")

    async def init(self):
        await self.ensure_keywords()
        await self.build_rtfm_lookup_table()

    @property
    def libraries(self):
        """return {
            'stable': 'https://discordpy.readthedocs.io/en/stable',
            'stable-jp': 'https://discordpy.readthedocs.io/ja/stable',
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
            'flogin': 'https://flogin.readthedocs.io/en/latest/',
            "aiohttp": "https://docs.aiohttp.org/en/stable",
        }"""
        items = self.settings.libraries or {}
        log.info(f"Libraries: {items!r}")
        return items

    @libraries.setter
    def libraries(self, new):
        self.settings.libraries = new

    @property
    def keywords(self):
        return list(self.libraries.keys()) + [self.main_kw]

    @property
    def main_kw(self) -> str:
        return self.settings.main_kw or "rtfm"

    @main_kw.setter
    def main_kw(self, value: str) -> None:
        self.settings.main_kw = value

    def parse_object_inv(
        self, stream: SphinxObjectFileReader, url: str
    ) -> dict[str, str]:
        # key: URL
        result: dict[str, str] = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if "zlib" not in line:
            raise RuntimeError(
                f"Invalid objects.inv file, not z-lib compatible. Line: {line}"
            )

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:
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

            result[f"{prefix}{key}"] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self):
        log.info("Starting to build cache...")
        cache: dict[str, dict[str, str]] = {}
        icons = {}

        for key, page in self.libraries.items():
            cache[key] = {}
            try:
                async with self.session.get(page + "/objects.inv") as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            "Cannot build rtfm lookup table, try again later."
                        )

                    stream = SphinxObjectFileReader(await resp.read())
                    # cache[key] = self.parse_object_inv(stream, page)
                    try:
                        cache[key] = self.parse_object_inv(stream, page)
                    except RuntimeError as e:
                        await self.api.show_notification(
                            "Rtfm",
                            f"The {key!r} library could not be parsed, and is not being cached.",
                        )
                        log.info(f"Sending could not be parsed notification: {e}")
                        continue

                icon = await asyncio.to_thread(get_icon, key, page)

                if icon:
                    icons[key] = str(icon)
            except aiohttp.InvalidUrlClientError:
                await self.api.show_error_message(
                    f"rtfm", f"Unable to cache {key!r} due to an invalid URL: {page!r}"
                )

        log.info(f"Done building cache.")
        self._rtfm_cache = cache
        self.icons = icons

    async def start(self):
        async with aiohttp.ClientSession() as cs:
            self.session = cs
            await self.start_webserver()
            await super().start()

    async def on_context_menu(self, data: list[str]):
        resp = await self.process_context_menus(data)
        if isinstance(resp, QueryResponse):
            for res in (ReloadCacheResult(), OpenSettingsResult()):
                self._results[res.slug] = res
                resp.results.append(res)
        return resp

    async def start_webserver(self):
        def write_libs(libs: list[dict[str, str]]):
            self.libraries = {lib["name"]: lib["url"] for lib in libs}
            log.info(f"--- {self.libraries=} ---")
            asyncio.create_task(self.ensure_keywords())

        await start_webserver(write_libs, self, run_forever=False)

    async def ensure_keywords(self):
        plugins = await self.api.get_all_plugins()
        for plugin in plugins:
            if plugin.id == self.metadata.id:
                log.info(f"Got plugin: {plugin!r}")
                keys = set(self.keywords)
                to_remove = set(plugin.keywords).difference(keys)
                to_add = keys.difference(plugin.keywords)

                for kw in to_remove:
                    await plugin.remove_keyword(kw)
                for kw in to_add:
                    await plugin.add_keyword(kw)
