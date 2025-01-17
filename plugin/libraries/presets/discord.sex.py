from __future__ import annotations

from plugin.libraries.algolia import AlgoliaBase, AlgoliaConfig


class DiscordSex(
    AlgoliaBase,
    config=AlgoliaConfig(
        url="https://jajudfjbi4-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for JavaScript (5.12.0); Lite (5.12.0); Browser; docsearch (3.6.3); docsearch-react (3.6.3)&x-algolia-api-key=13092021a31a84e0e8676c10affb9a16&x-algolia-application-id=JAJUDFJBI4",
        index_name="discord-usercers",
        kwargs={
            "attributesToRetrieve": [
                "hierarchy.lvl0",
                "hierarchy.lvl1",
                "hierarchy.lvl2",
                "hierarchy.lvl3",
                "hierarchy.lvl4",
                "hierarchy.lvl5",
                "hierarchy.lvl6",
                "content",
                "type",
                "url",
            ],
            "attributesToSnippet": [
                "hierarchy.lvl1:10",
                "hierarchy.lvl2:10",
                "hierarchy.lvl3:10",
                "hierarchy.lvl4:10",
                "hierarchy.lvl5:10",
                "hierarchy.lvl6:10",
                "content:10",
            ],
            "snippetEllipsisText": "…",
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
            "hitsPerPage": 20,
            "clickAnalytics": True,
        },
    ),
    base_url="https://docs.discord.sex",
    favicon_url="https://docs.discord.sex/favicon.ico",
): ...


preset = DiscordSex
