from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flogin import ExecuteResponse, Result

if TYPE_CHECKING:
    from .plugin import RtfmPlugin
else:
    RtfmPlugin = Any


class ReloadCacheResult(Result[RtfmPlugin]):
    def __init__(self) -> None:
        super().__init__("Reload cache", icon="assets/app.png")

    async def callback(self):
        assert self.plugin

        try:
            await self.plugin.build_rtfm_lookup_table()
        except RuntimeError as e:
            await self.plugin.api.show_error_message("rtfm", str(e))
        else:
            await self.plugin.api.show_notification(
                "rtfm", "Cache successfully reloaded"
            )
        return ExecuteResponse(hide=False)


class OpenSettingsResult(Result[RtfmPlugin]):
    def __init__(self) -> None:
        super().__init__(
            "Open Settings", icon="assets/app.png", sub="Open the settings webserver"
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_url("http://localhost:2907/")
        return ExecuteResponse()
