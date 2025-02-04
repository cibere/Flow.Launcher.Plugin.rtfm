from __future__ import annotations

from typing import TYPE_CHECKING

from yarl import URL

from . import doctypes, presets

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .library import Library, PartialLibrary
    from .preset import PresetLibrary

__all__ = "doc_types", "library_from_partial", "preset_docs"

doc_types: Iterable[type[Library]] = list(doctypes.fetch())
preset_docs: Iterable[type[PresetLibrary]] = list(presets.fetch())


def library_from_partial(lib: PartialLibrary) -> Library:
    if lib.type == "Preset":
        url = URL(lib.loc.rstrip("/"))
        for preset in preset_docs:
            if preset.validate_url(url):
                return preset.from_partial(lib)

        raise ValueError(f"Unknown preset for {url!r}")

    for doctype in doc_types:
        if lib.type == doctype.typename:
            return doctype.from_partial(lib)

    raise ValueError(f"Unsupported type {lib.type!r}")
