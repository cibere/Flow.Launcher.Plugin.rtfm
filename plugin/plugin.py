"""
Adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/api.py
Credits to Danny/Rapptz for the original rtfm code
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
from flogin import Plugin, QueryResponse

from .libraries import DocType, doc_types, library_from_partial
from .results import OpenLogFileResult, OpenSettingsResult, ReloadCacheResult
from .server.core import run_app as start_webserver
from .settings import RtfmBetterSettings

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from .library import Library, PartialLibrary

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

    @property
    def better_settings_file(self) -> Path:
        return Path("..", "..", "Settings", "Plugins", "rtfm", "better_settings.json")

    @property
    def libraries_database_file(self) -> Path:
        return Path("..", "..", "Settings", "Plugins", "rtfm", "libraries.json")

    def load_settings(self):
        try:
            with self.better_settings_file.open() as f:
                data = f.read()
        except FileNotFoundError:
            data = "{}"
        self.better_settings = RtfmBetterSettings.decode(data)

    def dump_settings(self):
        with self.better_settings_file.open("wb") as f:
            f.write(self.better_settings.encode())

    async def init(self) -> None:
        await self.webserver_ready_future
        await self.ensure_keywords()
        await self.build_rtfm_lookup_tables()

    @property
    def libraries(self) -> dict[str, Library]:
        if self._library_cache is None:
            libs = {
                lib.name: library_from_partial(lib)
                for lib in self.better_settings.libraries
            }
        else:
            libs = self._library_cache

        log.info(f"Libraries: {libs!r}")
        return libs

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
        self,
        library: Library,
        *,
        send_noti: bool = True,
        txt: str | None = None,
        wait: bool = False,
    ) -> str | None:
        log.info(f"Building cache for {library!r}")

        async def run(coro: Coroutine[Any, Any, Any]):
            if wait:
                return await coro
            asyncio.create_task(coro)

        if library.is_api is True:
            if txt is None:
                await run(library.fetch_icon())
                return
            coro = library.make_request(self.session, txt)
        else:
            coro = library.build_cache(self.session, self.webserver_port)

        try:
            await coro
        except Exception as e:
            log.exception(
                f"Sending could not be parsed notification for {library!r}", exc_info=e
            )
            txt = f"Unable to cache {library.name!r} due to the following error: {e}"
            if send_noti:
                await self.api.show_error_message("rtfm", txt)
            return txt
        await run(library.fetch_icon())

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

        async def write_libs(libs: list[PartialLibrary]) -> None:
            cache: dict[str, Library] = {}
            for lib in libs:
                if lib.type == "auto":
                    obj = await self.handle_auto_doctype(lib)
                    if obj is None:
                        await self.api.show_error_message(
                            "rtfm", f"Could not figure out how to parse {lib.name!r}"
                        )
                    else:
                        cache[lib.name] = obj
                else:
                    cache[lib.name] = library_from_partial(lib)
            self._library_cache = cache
            self.better_settings.libraries = [
                lib.to_partial() for lib in cache.values()
            ]
            self.dump_settings()
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

    async def handle_auto_doctype(self, data: PartialLibrary) -> DocType | None:
        for cls in doc_types:
            lib = cls.from_partial(data)
            try:
                await lib.build_cache(self.session, self.webserver_port)
            except:  # noqa: E722
                pass
            else:
                return lib
