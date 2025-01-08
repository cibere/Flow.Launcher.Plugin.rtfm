from __future__ import annotations

import logging

from flogin import Query, Result, SearchHandler

from ..fuzzy import finder as fuzzy_finder
from ..plugin import RtfmPlugin
from ..results import OpenRtfmResult

log = logging.getLogger(__name__)


class LookupHandler(SearchHandler[RtfmPlugin]):
    async def callback(self, query: Query):
        assert self.plugin

        text = query.text
        keyword = query.keyword

        try:
            library = self.plugin.libraries[keyword]
        except KeyError:
            return Result(
                f"Library '{keyword}' not found in settings", icon="Images/error.png"
            )

        if not library.use_cache:
            log.info(
                f"Library {library.name!r} not set to use cache, rebuilding for request"
            )
            msg = await self.plugin.refresh_library_cache(library, send_noti=False)
            if msg is not None:
                return Result(msg, icon=library.icon)

        if library.cache is None:
            return Result(
                f"Library '{library.name}' not found in cache", icon="Images/error.png"
            )

        if not text:
            return OpenRtfmResult(
                library=library,
                text="Open documentation",
                url=str(
                    library._build_url("index.html", self.plugin.webserver_port)
                    if library.path
                    else library.url
                ),
                score=1,
            )

        cache = list(library.cache.items())
        matches = fuzzy_finder(text, cache, key=lambda t: t[0])

        if len(matches) == 0:
            return Result("Could not find anything. Sorry.", icon=library.icon)

        return [
            OpenRtfmResult(
                library=library,
                url=match[1].replace("%23", "#"),
                text=match[0],
                score=100 - idx,
            )
            for idx, match in enumerate(matches)
        ]
