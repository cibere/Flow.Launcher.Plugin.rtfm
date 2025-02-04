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
            yield Result(
                f"Library '{keyword}' not found in settings", icon="Images/error.png"
            )
            return

        if not library.use_cache:
            log.debug(
                "Library %r not set to use cache, rebuilding for request", library.name
            )
            msg = await self.plugin.refresh_library_cache(
                library, send_noti=False, txt=query.text, wait=True
            )
            if msg is not None:
                yield Result(msg, icon=library.icon)
                return

        if library.cache is None:
            log.debug("Cache is `None`, refreshing")
            await self.plugin.refresh_library_cache(library)
            if library.cache is None:
                yield Result(
                    f"Library '{library.name}' not found in cache, and I was unable to build the cache.",
                    icon="Images/error.png",
                )
                return

        cache = list(library.cache.items())
        if library.is_api:
            matches = cache
        else:
            matches = fuzzy_finder(text, cache, key=lambda t: t[0])

        if len(matches) == 0:
            yield Result("Could not find anything. Sorry.", icon=library.icon)
            return

        for idx, (name, entry) in enumerate(reversed(matches)):
            if isinstance(entry, str):
                entry = Entry(name, entry)

            yield OpenRtfmResult(library=library, entry=entry, score=idx)
