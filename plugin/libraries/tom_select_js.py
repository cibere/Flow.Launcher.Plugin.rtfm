from __future__ import annotations

from typing import ClassVar

from .algolia import AlgoliaBase, AlgoliaConfig


class TomSelectJs(AlgoliaBase):
    classname: ClassVar[str] = "tom-select.js.org"
    base_url: ClassVar[str] = "https://tom-select.js.org/docs/"

    algolia_config: ClassVar[AlgoliaConfig] = AlgoliaConfig(
        url="https://bh4d9od16a-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript (lite) 3.30.0;docsearch.js 2.6.3&x-algolia-application-id=BH4D9OD16A&x-algolia-api-key=662e3a3a9d206ebad6d19f341b85acbd",
        index_name="tom-select",
        kwargs={"params": "query=te&hitsPerPage=20"},
    )
