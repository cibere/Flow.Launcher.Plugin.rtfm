from __future__ import annotations

import logging

from flogin import Query, Result, SearchHandler

from ..plugin import RtfmPlugin
from ..results import OpenRtfmResult

log = logging.getLogger(__name__)


class LookupHandler(SearchHandler[RtfmPlugin]):
    def condition(self, query: Query[list[str]]) -> bool:
        assert self.plugin

        if query.keyword != self.plugin.better_settings.main_kw:
            return True

        parts = query.text.split(" ")
        query.condition_data = parts
        log.info("lookup condition parts=%r", parts)
        return bool(parts)

    async def callback(self, query: Query[list[str]]):
        assert self.plugin

        if query.condition_data is not None:
            keyword, *raw_text = query.text.split(" ")
            text = " ".join(raw_text)
        else:
            keyword = query.keyword or "*"
            text = query.text

        try:
            manual = self.plugin.rtfm[keyword]
        except KeyError:
            return Result(
                f"Manual '{keyword}' not found in settings", icon="assets/error.png"
            )

        if not manual["dont_cache_results"] and (
            cached_results := self.plugin.result_cache[manual].get(query.text)
        ):
            log.debug("Returning results from result cache")
            return cached_results

        results = [
            OpenRtfmResult(
                manual=manual,
                entry=entry,
                score=idx,
            )
            async for idx, entry in manual.query(text)
        ]

        if not results:
            return Result("Could not find anything. Sorry.", icon=manual.icon_url)

        if manual["dont_cache_results"]:
            self.plugin.result_cache[manual][query.text] = results

        return results
