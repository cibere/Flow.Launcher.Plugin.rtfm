from __future__ import annotations

import asyncio
import logging
import secrets
import webbrowser

import pyperclip
from flogin import ExecuteResponse, Result

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Any, Unpack

    from flogin.jsonrpc.results import ResultConstructorKwargs  # noqa: TC002

    from .libraries.entry import Entry  # noqa: TC001
    from .libraries.library import Library  # noqa: TC001
    from .plugin import RtfmPlugin  # noqa: F401


log = logging.getLogger(__name__)


class BaseResult(Result["RtfmPlugin"]):
    def __modified_init(self, *args: Any, **kwargs: Any) -> None:
        if "auto_complete_text" in kwargs:
            raise RuntimeError(
                "'auto_complete_text' arg not supported as to add result slugs"
            )
        kwargs["auto_complete_text"] = secrets.token_hex(5)
        if "icon" not in kwargs:
            kwargs["icon"] = "assets/app.png"
        return super().__init__(*args, **kwargs)

    if not TYPE_CHECKING:
        __init__ = __modified_init


class ReloadCacheResult(BaseResult):
    def __init__(self) -> None:
        super().__init__(
            "Reload cache",
        )

    async def callback(self):
        assert self.plugin

        try:
            await self.plugin.build_rtfm_lookup_tables()
        except RuntimeError as e:
            await self.plugin.api.show_error_message("rtfm", str(e))
        else:
            await self.plugin.api.show_notification(
                "rtfm", "Cache successfully reloaded"
            )
        return ExecuteResponse(hide=False)


class OpenSettingsResult(BaseResult):
    def __init__(self) -> None:
        super().__init__(
            "Open Settings",
            sub="Open the settings webserver",
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_url(
            f"http://localhost:{self.plugin.webserver_port}/"
        )
        return ExecuteResponse()


class OpenLogFileResult(BaseResult):
    def __init__(self) -> None:
        super().__init__(
            "Open Log File",
            sub="Opens up the flogin log file",
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_directory(
            self.plugin.metadata.directory, "flogin.log"
        )
        return ExecuteResponse()


class OpenRtfmResult(BaseResult):
    def __init__(self, *, library: Library, entry: Entry, score: int) -> None:
        self.library = library
        self.url = entry.url.replace("%23", "#")
        self.entry = entry

        super().__init__(**entry.get_result_kwargs(library, score))

    async def callback(self) -> ExecuteResponse:
        assert self.plugin

        if self.library.path:
            log.debug("Opening URL: %r", self.url)
            await asyncio.to_thread(webbrowser.open, self.url)
        else:
            await self.plugin.api.open_url(self.url)

        return ExecuteResponse()

    async def context_menu(self):
        assert self.plugin

        yield CopyResult(self.url, title="Copy URL", icon="assets/copy.png", score=100)

        for result in self.entry.ctx_menu_factory(self.entry):
            yield result


class CopyResult(BaseResult):
    def __init__(self, text: str, **kwargs: Unpack[ResultConstructorKwargs]) -> None:
        super().__init__(**kwargs)
        self.text = text

    async def callback(self):
        assert self.plugin

        pyperclip.copy(self.text)
        await self.plugin.api.show_notification(
            "rtfm", f"Copied Text to clipboard: {self.text!r}"
        )
