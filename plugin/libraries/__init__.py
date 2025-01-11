from __future__ import annotations

from typing import TYPE_CHECKING

from .autohotkey import AutoHotkeyDocsV1, AutoHotkeyDocsV2
from .discord import Discord
from .discordsex import DiscordSex
from .flowlauncher import FlowLauncherDocs
from .intersphinx import SphinxLibrary
from .lua import Lua54
from .mdn import MdnDocs
from .mkdocs import Mkdocs
from .qmk import QmkDocs
from .ss64 import SS64Bash, SS64Mac, SS64NT, SS64PS

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..library import Library, PartialLibrary

DocType = SphinxLibrary | Mkdocs

doc_types: Iterable[type[DocType]] = DocType.__args__

PresetDocs = (
    AutoHotkeyDocsV1
    | AutoHotkeyDocsV2
    | MdnDocs
    | QmkDocs
    | FlowLauncherDocs
    | Lua54
    | Discord
    | DiscordSex
    | SS64Mac
    | SS64Bash
    | SS64NT
    | SS64PS
)

preset_docs: Iterable[type[PresetDocs]] = PresetDocs.__args__


def library_from_partial(lib: PartialLibrary) -> Library:
    classname = lib.type
    for iterable in (doc_types, preset_docs):
        for class_ in iterable:
            if classname == class_.classname:
                return class_.from_partial(lib)

    raise ValueError(f"Unsupported type {classname!r}")
