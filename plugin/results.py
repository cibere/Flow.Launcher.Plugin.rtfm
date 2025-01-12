from __future__ import annotations

import asyncio
import logging
import random
import webbrowser
from typing import TYPE_CHECKING

from flogin import ExecuteResponse, Result

if TYPE_CHECKING:
    from .libraries.library import Library
    from .plugin import RtfmPlugin  # noqa: F401

log = logging.getLogger(__name__)


class ReloadCacheResult(Result["RtfmPlugin"]):
    def __init__(self) -> None:
        super().__init__(
            "Reload cache",
            icon="assets/app.png",
            auto_complete_text="".join(random.choices("qwertyuiopasdfghjklzxcvbnm")),
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


class OpenSettingsResult(Result["RtfmPlugin"]):
    def __init__(self) -> None:
        super().__init__(
            "Open Settings",
            icon="assets/app.png",
            sub="Open the settings webserver",
            auto_complete_text="".join(random.choices("qwertyuiopasdfghjklzxcvbnm")),
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_url(
            f"http://localhost:{self.plugin.webserver_port}/"
        )
        return ExecuteResponse()


class OpenLogFileResult(Result["RtfmPlugin"]):
    def __init__(self) -> None:
        super().__init__(
            "Open Log File",
            icon="assets/app.png",
            sub="Opens up the flogin log file",
            auto_complete_text="".join(random.choices("qwertyuiopasdfghjklzxcvbnm")),
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_directory(
            self.plugin.metadata.directory, "flogin.log"
        )
        return ExecuteResponse()


class OpenRtfmResult(Result["RtfmPlugin"]):
    def __init__(self, *, library: Library, url: str, text: str, score: int) -> None:
        self.library = library
        self.url = url
        self.text = text

        super().__init__(
            title=text,
            auto_complete_text="".join(random.choices("qwertyuiopasdfghjklzxcvbnm")),
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
