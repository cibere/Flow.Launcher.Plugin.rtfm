from __future__ import annotations

import logging

from flogin import Query, SearchHandler

from ..plugin import RtfmPlugin
from ..results import (
    DisplayManualResult,
    OpenLogFileResult,
    OpenSettingsResult,
    ReloadCacheResult,
)

log = logging.getLogger(__name__)


class SettingsHandler(SearchHandler[RtfmPlugin]):
    def condition(self, query: Query):
        assert self.plugin

        return (
            (query.keyword or "*") == self.plugin.better_settings.main_kw
        ) and not query.text

    async def callback(self, query: Query):
        assert self.plugin

        return [
            OpenSettingsResult(),
            ReloadCacheResult(),
            OpenLogFileResult(),
            *(
                DisplayManualResult(manual, self.plugin)
                for manual in self.plugin.rtfm.manuals
            ),
        ]
