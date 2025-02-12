from __future__ import annotations

import logging

from flogin import Query, Result, SearchHandler

from ..fuzzy import finder as fuzzy_finder
from ..libraries.entry import Entry
from ..plugin import RtfmPlugin
from ..results import OpenRtfmResult

log = logging.getLogger(__name__)


class LookupHandler(SearchHandler[RtfmPlugin]):
    async def callback(self, query: Query):
        assert self.plugin

        text = query.text
        keyword = query.keyword or "*"

        try:
            library = self.plugin.libraries[keyword]
        except KeyError:
            return Result(
                f"Library '{keyword}' not found in settings", icon="Images/error.png"
            )

        if library.cache_results and (
            cached_results := library.result_cache.get(query.text)
        ):
            log.debug("Returning results from result cache")

            return cached_results

        if library.cache is None:
            log.debug("Refreshing cache for %r, cache or `None`", library.name)
            await self.plugin.refresh_library_cache(library)
            if library.cache is None:
                return Result(
                    f"Library '{library.name}' not found in cache, and I was unable to build the cache.",
                    icon="Images/error.png",
                )

        if library.is_api:
            await library.make_request(self.plugin.session, query.text)

        cache = list(library.cache.items())
        if library.is_api:
            matches = cache
        else:
            matches = fuzzy_finder(text, cache, key=lambda t: t[0])

        if len(matches) == 0:
            return Result("Could not find anything. Sorry.", icon=library.icon)

        results = [
            OpenRtfmResult(
                library=library,
                entry=(entry if isinstance(entry, Entry) else Entry(name, entry)),
                score=idx,
            )
            for idx, (name, entry) in enumerate(reversed(matches))
        ]

        if library.cache_results:
            library.result_cache[query.text] = results

        return results
