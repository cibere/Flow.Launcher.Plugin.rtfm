from __future__ import annotations

import logging
import re
from functools import partial

from flogin import KeywordCondition, Query, Result, SearchHandler
from flogin._types import SearchHandlerCondition

from ..fuzzy import finder as fuzzy_finder
from ..plugin import RtfmPlugin
from ..results import OpenSettingsResult, ReloadCacheResult

log = logging.getLogger(__name__)


class SettingsHandler(SearchHandler[RtfmPlugin]):
    def __init__(self):
        super().__init__(condition=self.condition)

    def condition(self, query: Query):
        assert self.plugin

        res = query.keyword == self.plugin.main_kw
        log.info(f"SettingsHandlerCondition = {res!r}")
        return res

    async def callback(self, query: Query):
        assert self.plugin

        return [OpenSettingsResult(), ReloadCacheResult()]
