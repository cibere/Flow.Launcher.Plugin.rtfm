from __future__ import annotations

from functools import partial

from flogin import Query, Result, SearchHandler

from ..fuzzy import finder as fuzzy_finder
from ..plugin import RtfmPlugin


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

        if library.cache is None:
            return Result(
                f"Library '{library.name}' not found in cache", icon="Images/error.png"
            )

        if not text:
            return Result.create_with_partial(
                partial(self.plugin.api.open_url, str(library.url)),
                title="Open documentation",
                icon=library.icon,
            )

        cache = list(library.cache.items())
        matches = fuzzy_finder(text, cache, key=lambda t: t[0])

        if len(matches) == 0:
            return Result("Could not find anything. Sorry.", icon=library.icon)

        return [
            Result.create_with_partial(
                partial(self.plugin.api.open_url, match[1]),
                title=match[0],
                score=100 - idx,
                icon=library.icon,
            )
            for idx, match in enumerate(matches)
        ]
