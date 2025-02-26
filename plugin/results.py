from __future__ import annotations

import logging
import secrets
from typing import TYPE_CHECKING, Any, Unpack

import pyperclip
from flogin import ExecuteResponse, Result
from yarl import URL

if TYPE_CHECKING:
    from flogin.jsonrpc.results import ResultConstructorKwargs

    from rtfm_lookup import Entry, Manual

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
            await self.plugin.rtfm.reload_cache()
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


def get_result_kwargs(
    entry: Entry, manual: Manual, score: int
) -> ResultConstructorKwargs:
    kwargs = entry.options.copy()
    kwargs["title"] = entry.text
    if "icon" not in kwargs:
        kwargs["icon"] = (
            manual.favicon_url
            or f"https://icons.duckduckgo.com/ip3/{URL(entry.url).host}.ico"
        )
    kwargs["score"] = score

    return kwargs  # pyright: ignore[reportReturnType]


class OpenRtfmResult(BaseResult):
    def __init__(self, *, manual: Manual, entry: Entry, score: int) -> None:
        self.manual = manual
        self.url = entry.url.replace("%23", "#")
        self.entry = entry

        super().__init__(**get_result_kwargs(entry, manual, score))

    async def callback(self) -> None:
        assert self.plugin
        assert self.plugin.last_query

        await self.plugin.api.open_url(self.url)

        if self.plugin.better_settings.reset_query:
            await self.plugin.last_query.update(text="")

    async def context_menu(self):
        assert self.plugin

        yield CopyResult(self.url, title="Copy URL", icon="assets/copy.png", score=100)

        # for result in self.entry.ctx_menu_factory(self.entry):
        #     yield result


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
