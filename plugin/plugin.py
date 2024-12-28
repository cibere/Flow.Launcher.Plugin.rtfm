"""
Adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import asyncio
import logging
import aiohttp
from flogin import Plugin, QueryResponse
from .results import OpenSettingsResult, ReloadCacheResult, OpenLogFileResult
from .server.core import run_app as start_webserver
from .settings import RtfmSettings
from .library import SphinxLibrary

log = logging.getLogger("rtfm")


class RtfmPlugin(Plugin[RtfmSettings]):
    _library_cache: dict[str, SphinxLibrary] | None = None
    session: aiohttp.ClientSession

    def __init__(self) -> None:
        super().__init__(settings_no_update=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.on_context_menu)
        self.register_event(self.init, "on_initialization")

    async def init(self):
        await self.ensure_keywords()
        await self.build_rtfm_lookup_tables()

    @property
    def libraries(self) -> dict[str, SphinxLibrary]:
        if self._library_cache is None:
            items = self.settings.libraries or {}
            self._library_cache = {
                lib: SphinxLibrary(lib, url, session=self.session)
                for lib, url in items.items()
            }

        log.info(f"Libraries: {self._library_cache!r}")
        return self._library_cache

    @libraries.setter
    def libraries(self, data: dict[str, str]):
        self.settings.libraries = data
        self._library_cache = {
            lib: SphinxLibrary(lib, url, session=self.session)
            for lib, url in data.items()
        }

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

    async def refresh_library_cache(self, library: SphinxLibrary) -> bool:
        try:
            await library.build_cache()
        except Exception as e:
            log.exception(
                f"Sending could not be parsed notification for {library!r}", exc_info=e
            )
            await self.api.show_error_message(
                f"rtfm",
                f"Unable to cache {library.name!r} due to the following error: {e}",
            )
            return False
        await library.fetch_icon()
        return True

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
