from __future__ import annotations

from functools import partial

from flogin import Query, Result, SearchHandler

from ..fuzzy import finder as fuzzy_finder
from ..plugin import RtfmPlugin


class LookupHandler(SearchHandler[RtfmPlugin]):
    async def callback(self, query: Query):
        assert self.plugin

        text = query.text
        library = query.keyword

        try:
            url = self.plugin.libraries[library]
        except KeyError:
            return Result(
                f"Library '{library}' not found in settings", icon="Images/error.png"
            )

        if text is None:
            return Result.create_with_partial(
                partial(self.plugin.api.open_url, url), title="Open documentation"
            )

        if not hasattr(self.plugin, "_rtfm_cache"):
            await self.plugin.build_rtfm_lookup_table()

        try:
            cache = list(self.plugin._rtfm_cache[library].items())
        except KeyError:
            return Result(
                f"Library '{library}' not found in cache", icon="Images/error.png"
            )

        matches = fuzzy_finder(text, cache, key=lambda t: t[0])

        if len(matches) == 0:
            return "Could not find anything. Sorry."

        return [
            Result.create_with_partial(
                partial(self.plugin.api.open_url, match[1]),
                title=match[0],
                score=100 - idx,
                icon=self.plugin.icons.get(library),
            )
            for idx, match in enumerate(matches)
        ]
