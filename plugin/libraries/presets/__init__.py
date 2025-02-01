from __future__ import annotations

from plugin.loader import load_item_or_items

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..preset import PresetLibrary  # noqa: TC001


def fetch() -> list[type[PresetLibrary]]:
    return list(load_item_or_items("preset", __file__))


parser_url_format = "https://github.com/cibere/Flow.Launcher.Plugin.rtfm/tree/main/plugin/libraries/presets/{entry.__module__}.py"
