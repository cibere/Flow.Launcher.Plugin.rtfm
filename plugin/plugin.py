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
from .settings import RtfmSettings

if TYPE_CHECKING:
    from .library import Library

log = logging.getLogger("rtfm")


class RtfmPlugin(Plugin[RtfmSettings]):
    _library_cache: dict[str, Library] | None = None
    session: aiohttp.ClientSession
    webserver_port: int

    def __init__(self) -> None:
        super().__init__(settings_no_update=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.on_context_menu)
        self.register_event(self.init, "on_initialization")

    def load_libraries(self) -> dict[str, Library]:
        """from .libraries.autohotkey import AutoHotkeyDocsV1, AutoHotkeyDocsV2
        from .libraries.mdn import MdnDocs
        from .libraries.mkdocs import Mkdocs
        from .libraries.qmk import QmkDocs

        log.info("Loading a set new of libraries")
        return {
            "ahk1": AutoHotkeyDocsV1("ahk1", use_cache=True),
            "ahk2": AutoHotkeyDocsV2("ahk2", use_cache=True),
            "qmk": QmkDocs("qmk", use_cache=True),
            "ruff": Mkdocs(
                "mkdocs", URL("https://docs.astral.sh/ruff/"), use_cache=True
            ),
            "mdn": MdnDocs("mdn", use_cache=True),
        }"""
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
        await self.ensure_keywords()
        await self.build_rtfm_lookup_tables()
        self.check_for_legacy_settings()

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
        return self.settings.main_kw or "rtfm"

    @main_kw.setter
    def main_kw(self, value: str) -> None:
        self.settings.main_kw = value

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
            await self.start_webserver()
            await super().start()

    async def on_context_menu(self, data: list[str]):
        resp = await self.process_context_menus(data)
        if isinstance(resp, QueryResponse):
            for res in (ReloadCacheResult(), OpenSettingsResult(), OpenLogFileResult()):
                self._results[res.slug] = res
                resp.results.append(res)
        return resp

    async def start_webserver(self) -> None:
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
