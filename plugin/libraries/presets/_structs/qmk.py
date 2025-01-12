from __future__ import annotations

import msgspec


class QmkLocalSearchField(msgspec.Struct):
    title: str
    titles: list[str]


class QmkLocalSearchData(msgspec.Struct):
    documentIds: dict[str, str]
    storedFields: dict[str, QmkLocalSearchField]
