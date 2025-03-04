from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ParamSpec

from flogin import ErrorResponse, Plugin, QueryResponse

from .server.core import run_app as start_webserver
from .settings import RtfmBetterSettings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine

    from rtfm_lookup import Manual, RtfmManager

    from .logs import Logs

log = logging.getLogger("rtfm")
P = ParamSpec("P")


class RtfmPlugin(Plugin[None]):  # type: ignore
    webserver_port: int
    webserver_ready_future: asyncio.Future
    better_settings: RtfmBetterSettings
    logs: Logs
    rtfm: RtfmManager

    def __init__(self) -> None:
        super().__init__(settings_no_update=True, disable_log_override_files=True)

        from .handlers.lookup_handler import LookupHandler
        from .handlers.settings_handler import SettingsHandler

        self.register_search_handlers(SettingsHandler(), LookupHandler())
        self.register_event(self.init, "on_initialization")
        self.webserver_ready_future = asyncio.Future()
        self.result_cache = defaultdict(dict)

        self.process_context_menus = self._simple_view_converter(
            self.process_context_menus
        )
        self.process_search_handlers = self._simple_view_converter(
            self.process_search_handlers
        )

    @property
    def better_settings_file(self) -> Path:
        return Path("..", "..", "Settings", "Plugins", "rtfm", "better_settings.json")

    def load_settings(self):
        try:
            with self.better_settings_file.open() as f:
                data = f.read()
        except FileNotFoundError:
            self.better_settings = RtfmBetterSettings()
        else:
            self.better_settings = RtfmBetterSettings.decode(data)

        self.rtfm.load_partials(*self.better_settings.manuals)

    def dump_settings(self):
        with self.better_settings_file.open("wb") as f:
            f.write(self.better_settings.encode())

    async def init(self) -> None:
        await self.webserver_ready_future
        await self.ensure_keywords()
        self.rtfm.trigger_cache_reload()

    async def refresh_manual_cache(
        self,
        manual: Manual,
        *,
        send_noti: bool = True,
    ) -> None | str:
        log.debug("Building cache for %r", manual)
        self.result_cache[manual] = {}

        try:
            await manual.refresh_cache()
        except Exception as e:
            log.exception(
                "Sending could not be parsed notification for %r", manual, exc_info=e
            )
            txt = f"Unable to cache {manual.name!r} due to the following error: {e}"
            if send_noti:
                await self.api.show_error_message("rtfm", txt)
            return txt

    @property
    def keywords(self):
        return [*list(self.rtfm.manuals.keys()), self.better_settings.main_kw]

    async def start_webserver(self) -> None:
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
