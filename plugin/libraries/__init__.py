from .autohotkey import AutoHotkeyDocsV1, AutoHotkeyDocsV2
from .intersphinx import SphinxLibrary
from .mdn import MdnDocs
from .mkdocs import Mkdocs
from .qmk import QmkDocs

doc_types = (
    SphinxLibrary,
    Mkdocs,
)

custom_doc_implementations = (
    AutoHotkeyDocsV1,
    AutoHotkeyDocsV2,
    MdnDocs,
    QmkDocs,
)
