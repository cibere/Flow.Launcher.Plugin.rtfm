from __future__ import annotations

import logging

from flogin import Query, SearchHandler

from ..plugin import RtfmPlugin
from ..results import OpenLogFileResult, OpenSettingsResult, ReloadCacheResult

log = logging.getLogger(__name__)


class SettingsHandler(SearchHandler[RtfmPlugin]):
    def __init__(self) -> None:
        super().__init__(condition=self.condition)

    def condition(self, query: Query):
        assert self.plugin

        return query.keyword == self.plugin.main_kw

    async def callback(self, query: Query):
        assert self.plugin

        return [OpenSettingsResult(), ReloadCacheResult(), OpenLogFileResult()]
