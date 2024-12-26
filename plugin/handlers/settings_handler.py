from __future__ import annotations

import logging

from flogin import Query, SearchHandler

from ..plugin import RtfmPlugin
from ..results import OpenSettingsResult, ReloadCacheResult, OpenLogFileResult

log = logging.getLogger(__name__)


class SettingsHandler(SearchHandler[RtfmPlugin]):
    def __init__(self):
        super().__init__(condition=self.condition)

    def condition(self, query: Query):
        assert self.plugin

        res = query.keyword == self.plugin.main_kw
        return res

    async def callback(self, query: Query):
        assert self.plugin

        return [OpenSettingsResult(), ReloadCacheResult(), OpenLogFileResult()]