from collections.abc import Iterable

from .autohotkey import AutoHotkeyDocsV1, AutoHotkeyDocsV2
from .intersphinx import SphinxLibrary
from .mdn import MdnDocs
from .mkdocs import Mkdocs
from .qmk import QmkDocs
from .flowlauncher import FlowLauncherDocs

DocType = SphinxLibrary | Mkdocs

doc_types: Iterable[DocType] = DocType.__args__

PresetDocs = AutoHotkeyDocsV1 | AutoHotkeyDocsV2 | MdnDocs | QmkDocs | FlowLauncherDocs

preset_docs: Iterable[PresetDocs] = PresetDocs.__args__


def library_from_dict(lib: dict[str, str | bool]) -> DocType | PresetDocs:
    classname = lib["type"]

    for iterable in (doc_types, preset_docs):
        for class_ in iterable:
            if classname == class_.classname:
                return class_.from_dict(lib)

    raise ValueError(f"Unsupported type {classname!r}")
