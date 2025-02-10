from __future__ import annotations

from typing import TYPE_CHECKING

from . import doctypes

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .library import Library, PartialLibrary

doc_types: Iterable[type[Library]] = list(doctypes.fetch())


def library_from_partial(lib: PartialLibrary) -> Library:
    for doctype in doc_types:
        if lib.type == doctype.typename:
            return doctype.from_partial(lib)

    raise ValueError(f"Unsupported type {lib.type!r}")
