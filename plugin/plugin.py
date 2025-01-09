"""
Adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import asyncio
import logging
import os
import pickle
from typing import TYPE_CHECKING, Any

import aiohttp
from flogin import Plugin, QueryResponse

from .libraries import library_from_dict
from .results import OpenLogFileResult, OpenSettingsResult, ReloadCacheResult
from .server.core import run_app as start_webserver
from .settings import RtfmBetterSettings

if TYPE_CHECKING:
    from .library import Library

log = logging.getLogger("rtfm")


class RtfmPlugin(Plugin[None]):  # type: ignore
    _library_cache: dict[str, Library] | None = None
    session: aiohttp.ClientSession
    webserver_port: int
    webserver_ready_future: asyncio.Future
    better_settings: RtfmBetterSettings

    def __init__(self) -> None:
        super().__init__(settings_no_update=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.on_context_menu)
        self.register_event(self.init, "on_initialization")
        self.load_settings()

    def load_settings(self):
        fp = os.path.join(
            "..", "..", "Settings", "Plugins", "rtfm", "better_settings.json"
        )
        try:
            with open(fp) as f:
                data = f.read()
        except FileNotFoundError:
            data = "{}"
        self.better_settings = RtfmBetterSettings.decode(data)

    def dump_settings(self):
        fp = os.path.join(
            "..", "..", "Settings", "Plugins", "rtfm", "better_settings.json"
        )
        with open(fp, "wb") as f:
            f.write(self.better_settings.encode())

    def load_libraries(self) -> dict[str, Library]:
        fp = os.path.join(
            "..", "..", "Settings", "Plugins", self.metadata.name, "libraries.pickle"
        )
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                self._library_cache = libs = pickle.load(f)
        else:
            self._library_cache = libs = {}

        return libs

    def dump_libraries(self) -> None:
        libs = self.libraries

        fp = os.path.join(
            "..", "..", "Settings", "Plugins", self.metadata.name, "libraries.pickle"
        )
        with open(fp, "wb") as f:
            pickle.dump(libs, f)

    async def init(self) -> None:
        await self.webserver_ready_future
        await self.ensure_keywords()
        await self.build_rtfm_lookup_tables()

    @property
    def libraries(self) -> dict[str, Library]:
        if self._library_cache is None:
            self._library_cache = libs = self.load_libraries()
        else:
            libs = self._library_cache

        log.info(f"Libraries: {libs!r}")
        return libs

    @libraries.setter
    def libraries(self, data: list[dict[str, Any]]) -> None:
        self._library_cache = {lib["name"]: library_from_dict(lib) for lib in data}
        self.dump_libraries()

    @property
    def keywords(self):
        return [*list(self.libraries.keys()), self.main_kw]

    @property
    def main_kw(self) -> str:
        return self.better_settings.main_kw

    @main_kw.setter
    def main_kw(self, value: str) -> None:
        self.better_settings.main_kw = value
        self.dump_settings()

    @property
    def static_port(self) -> int:
        return self.better_settings.static_port

    @static_port.setter
    def static_port(self, value: int) -> None:
        self.better_settings.static_port = value
        self.dump_settings()

    async def build_rtfm_lookup_tables(self) -> None:
        log.info("Starting to build cache...")

        await asyncio.gather(
            *(self.refresh_library_cache(lib) for lib in self.libraries.values())
        )

        log.info("Done building cache.")

    async def refresh_library_cache(
        self, library: Library, *, send_noti: bool = True
    ) -> str | None:
        log.info(f"Building cache for {library!r}")

        try:
            await library.build_cache(self.session, self.webserver_port)
        except Exception as e:
            log.exception(
                f"Sending could not be parsed notification for {library!r}", exc_info=e
            )
            txt = f"Unable to cache {library.name!r} due to the following error: {e}"
            if send_noti:
                await self.api.show_error_message("rtfm", txt)
            return txt
        await library.fetch_icon()

    async def start(self) -> None:
        async with aiohttp.ClientSession() as cs:
            self.session = cs
            asyncio.create_task(self.start_webserver())
            await super().start()

    async def on_context_menu(self, data: list[str]):
        resp = await self.process_context_menus(data)
        if isinstance(resp, QueryResponse):
            for res in (ReloadCacheResult(), OpenSettingsResult(), OpenLogFileResult()):
                self._results[res.slug] = res
                resp.results.append(res)
        return resp

    async def start_webserver(self) -> None:
        self.webserver_ready_future = asyncio.Future()

        def write_libs(libs: list[dict[str, str]]) -> None:
            self.libraries = libs
            log.info(f"--- {self.libraries=} ---")
            asyncio.create_task(self.ensure_keywords())

        await start_webserver(write_libs, self, run_forever=False)

    async def ensure_keywords(self) -> None:
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
