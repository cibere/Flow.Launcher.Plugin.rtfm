from __future__ import annotations

import logging
import secrets
from typing import TYPE_CHECKING, Any, Unpack

import pyperclip
from flogin import ExecuteResponse, Result

if TYPE_CHECKING:
    from flogin.jsonrpc.results import ResultConstructorKwargs
    from rtfm_lookup import Entry, Manual

    from .plugin import RtfmPlugin


log = logging.getLogger(__name__)


class BaseResult(Result["RtfmPlugin"]):
    def __modified_init(self, *args: Any, **kwargs: Any) -> None:
        if "auto_complete_text" not in kwargs:
            kwargs["auto_complete_text"] = secrets.token_hex(5)
        if "icon" not in kwargs:
            kwargs["icon"] = "assets/app.png"
        return super().__init__(*args, **kwargs)

    if not TYPE_CHECKING:
        __init__ = __modified_init


class ReloadCacheResult(BaseResult):
    def __init__(self) -> None:
        super().__init__("Reload cache", score=1000)

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
        super().__init__("Open Settings", sub="Open the settings webserver", score=1000)

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_url(
            f"http://localhost:{self.plugin.webserver_port}/"
        )
        return ExecuteResponse()


class OpenLogFileResult(BaseResult):
    def __init__(self) -> None:
        super().__init__(
            "Open Log File", sub="Opens up the flogin log file", score=1000
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
        kwargs["icon"] = manual.icon_url
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


class DisplayManualResult(BaseResult):
    def __init__(self, manual: Manual, plugin: RtfmPlugin) -> None:
        self.new_query = (
            f"{plugin.better_settings.main_kw} {manual.name}"
            if plugin.better_settings.condense_keywords
            else ("" if manual.name == "*" else manual.name)
        ) + " "
        super().__init__(
            title=manual.name,
            sub=str(manual.loc),
            icon=manual.icon_url,
            auto_complete_text=self.new_query,
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.change_query(self.new_query)
        return False
