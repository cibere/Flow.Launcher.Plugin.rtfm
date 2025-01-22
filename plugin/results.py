from __future__ import annotations

import asyncio
import logging
import secrets
import webbrowser
from typing import TYPE_CHECKING, Any

from flogin import ExecuteResponse, Result

if TYPE_CHECKING:
    from .libraries.library import Library
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
    def __init__(self, *, library: Library, url: str, text: str, score: int) -> None:
        self.library = library
        self.url = url
        self.text = text

        super().__init__(
            title=text,
            score=score,
            icon=library.icon,
        )

    async def callback(self) -> ExecuteResponse:
        assert self.plugin

        if self.library.path:
            log.info(f"Opening URL: {self.url!r}")
            await asyncio.to_thread(webbrowser.open, self.url)
        else:
            await self.plugin.api.open_url(self.url)

        return ExecuteResponse()
