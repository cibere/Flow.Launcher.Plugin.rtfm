from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from aiohttp import ClientSession

    from ....entry import Entry
    from ..structs import ApiIndex

from .algolia import Algolia
from .github import Github
from .mathworks import Mathworks

api_handlers: dict[
    str, Callable[[str, ApiIndex, ClientSession], Awaitable[dict[str, str | Entry]]]
] = {"Algolia": Algolia, "Github": Github, "Mathworks": Mathworks}
