from __future__ import annotations

from typing import TYPE_CHECKING

from yarl import URL

from .intersphinx import SphinxLibrary
from .mkdocs import Mkdocs
from .presets._loader import built_presets

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .library import Library, PartialLibrary
    from .preset import PresetLibrary

doc_types: Iterable[type[Library]] = (
    Mkdocs,
    SphinxLibrary,
)
preset_docs: Iterable[type[PresetLibrary]] = list(built_presets())


def library_from_partial(lib: PartialLibrary) -> Library:
    if lib.type == "Preset":
        url = URL(lib.loc)
        for preset in preset_docs:
            if preset.validate_url(url):
                return preset.from_partial(lib)

    for doctype in doc_types:
        if lib.type == doctype.typename:
            return doctype.from_partial(lib)

    raise ValueError(f"Unsupported type {lib.type!r}")
