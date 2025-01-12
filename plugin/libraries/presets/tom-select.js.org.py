from __future__ import annotations

from plugin.libraries.algolia import AlgoliaBase, AlgoliaConfig


class TomSelectJs(
    AlgoliaBase,
    config=AlgoliaConfig(
        url="https://bh4d9od16a-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript (lite) 3.30.0;docsearch.js 2.6.3&x-algolia-application-id=BH4D9OD16A&x-algolia-api-key=662e3a3a9d206ebad6d19f341b85acbd",
        index_name="tom-select",
        kwargs={"params": "query=te&hitsPerPage=20"},
    ),
    base_url="https://tom-select.js.org/docs/",
): ...


preset = TomSelectJs
