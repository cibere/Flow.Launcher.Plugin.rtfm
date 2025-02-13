from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ParamSpec

import aiohttp
from flogin import ErrorResponse, Plugin, QueryResponse
from yarl import URL

from .better_lock import BetterLock
from .libraries import doc_types, library_from_partial
from .server.core import run_app as start_webserver
from .settings import RtfmBetterSettings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine

    from .libraries.library import Library, PartialLibrary
    from .logs import Logs

log = logging.getLogger("rtfm")
P = ParamSpec("P")


class RtfmPlugin(Plugin[None]):  # type: ignore
    _library_cache: dict[str, Library] | None = None
    session: aiohttp.ClientSession
    webserver_port: int
    webserver_ready_future: asyncio.Future
    better_settings: RtfmBetterSettings
    cache_lock: BetterLock
    logs: Logs

    def __init__(self) -> None:
        super().__init__(settings_no_update=True, disable_log_override_files=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.init, "on_initialization")
        self.load_settings()
        self.cache_lock = BetterLock()

        self.process_context_menus = self._simple_view_converter(
            self.process_context_menus
        )
        self.process_search_handlers = self._simple_view_converter(
            self.process_search_handlers
        )

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

        if self.better_settings.version != self.metadata.version:
            self.better_settings.version = self.metadata.version
            self.dump_settings()

    @property
    def libraries(self) -> dict[str, Library]:
        if self._library_cache is None:
            self._library_cache = libs = {}
            for lib in self.better_settings.libraries:
                try:
                    libs[lib.name] = library_from_partial(lib)
                except ValueError as e:  # noqa: PERF203
                    asyncio.create_task(
                        self.api.show_error_message(
                            "rtfm",
                            f"The {lib.name!r} manual is being removed due to an error while attempting to load it: {e}",
                        )
                    )
        else:
            libs = self._library_cache

        log.debug("Libraries: %r", libs)
        return libs

    @property
    def keywords(self):
        return [*list(self.libraries.keys()), self.better_settings.main_kw]

    async def build_rtfm_lookup_tables(self) -> None:
        log.debug("Starting to build cache...")

        if self.cache_lock.locked():
            log.exception("Cache is already building, awaiting until complete")
            return await self.cache_lock.wait()

        async with self.cache_lock:
            await asyncio.gather(
                *(self.refresh_library_cache(lib) for lib in self.libraries.values())
            )

        log.debug("Done building cache.")

    async def refresh_library_cache(
        self,
        library: Library,
        *,
        send_noti: bool = True,
        wait: bool = False,
    ) -> str | None:
        log.debug("Building cache for %r", library)
        library.result_cache = {}

        async def run(coro: Coroutine[Any, Any, Any]):
            if wait:
                return await coro
            asyncio.create_task(coro)

        try:
            await library.build_cache(self.session, self.webserver_port)
        except Exception as e:
            log.exception(
                "Sending could not be parsed notification for %r", library, exc_info=e
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

    async def update_libraries(self, libs: list[PartialLibrary]) -> None:
        cache: dict[str, Library] = {}
        for lib in libs:
            cache[lib.name] = library_from_partial(lib)
        self._library_cache = cache
        self.better_settings.libraries = [lib.to_partial() for lib in cache.values()]
        self.dump_settings()
        log.debug("libraries: %r", self.libraries)
        asyncio.create_task(self.ensure_keywords())

    async def start_webserver(self) -> None:
        self.webserver_ready_future = asyncio.Future()

        await start_webserver(self, run_forever=False)

    async def ensure_keywords(self) -> None:
        plugins = await self.api.get_all_plugins()
        for plugin in plugins:
            if plugin.id == self.metadata.id:
                log.debug("Got plugin: %r", plugin)
                keys = set(self.keywords)
                to_remove = set(plugin.keywords).difference(keys)
                to_add = keys.difference(plugin.keywords)

                for kw in to_remove:
                    await plugin.remove_keyword(kw)
                for kw in to_add:
                    await plugin.add_keyword(kw)

    async def handle_auto_doctype(self, data: PartialLibrary) -> Library | None:
        for cls in doc_types:
            lib = cls.from_partial(data)
            try:
                await lib.build_cache(self.session, self.webserver_port)
            except:  # noqa: E722, S110
                pass
            else:
                return lib

    def convert_raw_loc(self, loc: str) -> URL | Path:
        if loc.startswith(("http://", "https://")):
            return URL(loc)
        if loc.startswith("file:///"):
            return Path(URL(loc).path.strip("/"))
        if (
            loc[0] in "QWERTYUIOPASDFGHJKLZXCVBNM"
            and loc[1] == ":"
            and loc[2] in ("/", "\\")
        ):
            return Path(loc)
        parts = loc.split("/")
        return URL.build(scheme="https", host=parts.pop(0), path="/" + "/".join(parts))

    async def get_library_from_url(self, name: str, raw_url: str) -> Library | None:
        loc = self.convert_raw_loc(raw_url.rstrip("/"))
        log.debug("Getting library from url: %r", loc)
        is_path: bool = isinstance(loc, Path)

        for Doctype in doc_types:
            if is_path is True and Doctype.supports_local is False:
                continue
            lib = Doctype(name, loc, cache_results=True)
            try:
                log.debug("Trying doctype: %r", Doctype)
                await lib.build_cache(self.session, self.webserver_port)
            except Exception as e:
                log.exception("Failed to build cache for library: %r", name, exc_info=e)
            else:
                return lib

    def _simple_view_converter(
        self, original: Callable[P, Awaitable[QueryResponse | ErrorResponse]]
    ) -> Callable[P, Coroutine[Any, Any, QueryResponse | ErrorResponse]]:
        async def inner(
            *args: P.args, **kwargs: P.kwargs
        ) -> QueryResponse | ErrorResponse:
            resp = await original(*args, **kwargs)
            if isinstance(resp, QueryResponse) and self.better_settings.simple_view:
                for res in resp.results:
                    res.sub = None
            return resp

        return inner
