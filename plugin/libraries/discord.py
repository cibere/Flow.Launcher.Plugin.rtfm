from __future__ import annotations

from typing import ClassVar

from .algolia import AlgoliaBase, AlgoliaConfig


class Discord(AlgoliaBase):
    classname: ClassVar[str] = "discord.dev"
    favicon_url: ClassVar[str] | None = "https://discord.dev"
    base_url: ClassVar[str] = "https://discord.com/developers/docs"
    algolia_config: ClassVar[AlgoliaConfig] = AlgoliaConfig(
        url="https://7tyoyf10z2-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for JavaScript (4.23.3); Browser (lite); docsearch (3.3.1); docsearch-react (3.3.1)&x-algolia-api-key=786517d17e19e9d306758dd276bc6574&x-algolia-application-id=7TYOYF10Z2",
        index_name="discord",
        kwargs={
            "params": "attributesToRetrieve=%5B%22hierarchy.lvl0%22%2C%22hierarchy.lvl1%22%2C%22hierarchy.lvl2%22%2C%22hierarchy.lvl3%22%2C%22hierarchy.lvl4%22%2C%22hierarchy.lvl5%22%2C%22hierarchy.lvl6%22%2C%22content%22%2C%22type%22%2C%22url%22%5D&attributesToSnippet=%5B%22hierarchy.lvl1%3A10%22%2C%22hierarchy.lvl2%3A10%22%2C%22hierarchy.lvl3%3A10%22%2C%22hierarchy.lvl4%3A10%22%2C%22hierarchy.lvl5%3A10%22%2C%22hierarchy.lvl6%3A10%22%2C%22content%3A10%22%5D&snippetEllipsisText=%E2%80%A6&highlightPreTag=%3Cmark%3E&highlightPostTag=%3C%2Fmark%3E&hitsPerPage=20"
        },
    )
