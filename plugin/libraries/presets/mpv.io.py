from __future__ import annotations

from plugin.libraries.rtfm_index import RtfmIndexBase


class MpvIoMaster(
    RtfmIndexBase,
    name="mpv.io-master",
    url="https://mpv.io/manual/master/",
    is_variant=True,
): ...


class MpvIoStable(
    RtfmIndexBase,
    name="mpv.io-stable",
    url="https://mpv.io/manual/stable/",
    is_variant=True,
): ...


presets = (MpvIoMaster, MpvIoStable)
