from __future__ import annotations

import logging

from flogin import Query, Result, SearchHandler

from ..plugin import RtfmPlugin
from ..results import OpenRtfmResult

log = logging.getLogger(__name__)


class LookupHandler(SearchHandler[RtfmPlugin]):
    async def callback(self, query: Query):
        assert self.plugin

        text = query.text
        keyword = query.keyword or "*"

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
            return Result("Could not find anything. Sorry.", icon=manual.favicon_url)

        if manual["dont_cache_results"]:
            self.plugin.result_cache[manual][query.text] = results

        return results
