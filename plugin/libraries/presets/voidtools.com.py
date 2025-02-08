from __future__ import annotations

from plugin.libraries.rtfm_index import RtfmIndexBase


class VoidTools(
    RtfmIndexBase,
    name="voidtools",
    url="https://www.voidtools.com/support/everything",
): ...


preset = VoidTools
