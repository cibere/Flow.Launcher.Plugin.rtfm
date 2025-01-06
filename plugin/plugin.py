"""
Adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import asyncio
import logging, pickle, os
import aiohttp
from typing import Any
from flogin import Plugin, QueryResponse
from .results import OpenSettingsResult, ReloadCacheResult, OpenLogFileResult
from .server.core import run_app as start_webserver
from .settings import RtfmSettings
from .library import SphinxLibrary

log = logging.getLogger("rtfm")


class RtfmPlugin(Plugin[RtfmSettings]):
    _library_cache: dict[str, SphinxLibrary] | None = None
    session: aiohttp.ClientSession
    webserver_port: int

    def __init__(self) -> None:
        super().__init__(settings_no_update=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.on_context_menu)
        self.register_event(self.init, "on_initialization")

    def load_libraries(self) -> dict[str, SphinxLibrary]:
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

    async def init(self):
        await self.ensure_keywords()
        await self.build_rtfm_lookup_tables()
        self.check_for_legacy_settings()

    @property
    def libraries(self) -> dict[str, SphinxLibrary]:
        if self._library_cache is None:
            libs = self.load_libraries()
        else:
            libs = self._library_cache

        log.info(f"Libraries: {libs!r}")
        return libs

    @libraries.setter
    def libraries(self, data: list[dict[str, Any]]):
        self._library_cache = {
            lib["name"]: SphinxLibrary.from_dict(lib) for lib in data
        }
        self.dump_libraries()

    @property
    def keywords(self):
        return list(self.libraries.keys()) + [self.main_kw]

    @property
    def main_kw(self) -> str:
        return self.settings.main_kw or "rtfm"

    @main_kw.setter
    def main_kw(self, value: str) -> None:
        self.settings.main_kw = value

    async def build_rtfm_lookup_tables(self):
        log.info("Starting to build cache...")

        await asyncio.gather(
            *(self.refresh_library_cache(lib) for lib in self.libraries.values())
        )

        log.info(f"Done building cache.")

    async def refresh_library_cache(
        self, library: SphinxLibrary, *, send_noti: bool = True
    ) -> str | None:
        try:
            await library.build_cache(self.session, self.webserver_port)
        except Exception as e:
            log.exception(
                f"Sending could not be parsed notification for {library!r}", exc_info=e
            )
            txt = f"Unable to cache {library.name!r} due to the following error: {e}"
            if send_noti:
                await self.api.show_error_message(f"rtfm", txt)
            return txt
        await library.fetch_icon()

    async def start(self):
        async with aiohttp.ClientSession() as cs:
            self.session = cs
            await self.start_webserver()
            await super().start()

    async def on_context_menu(self, data: list[str]):
        resp = await self.process_context_menus(data)
        if isinstance(resp, QueryResponse):
            for res in (ReloadCacheResult(), OpenSettingsResult(), OpenLogFileResult()):
                self._results[res.slug] = res
                resp.results.append(res)
        return resp

    async def start_webserver(self):
        def write_libs(libs: list[dict[str, str]]):
            self.libraries = libs
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

    def check_for_legacy_settings(self):
        libs = self.settings.libraries
        if libs is None:
            return log.info("No legacy lib settings found")

        log.info("Legacy library settings found, converting to current format")
        self.libraries = [
            {"name": name, "loc": loc, "use_cache": True} for name, loc in libs.items()
        ]
        self.settings.libraries = None

        log.info("Done converting legacy library settings")
