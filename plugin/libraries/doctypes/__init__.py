from __future__ import annotations

from ...loader import load_item_or_items

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..library import Library  # noqa: TC001# noqa: TC001


def fetch() -> list[type[Library]]:
    return list(load_item_or_items("doctype", __file__))
