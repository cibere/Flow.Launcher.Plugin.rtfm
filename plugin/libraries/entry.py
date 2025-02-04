from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

if TYPE_CHECKING:
    from flogin import ResultConstructorKwargs

    from .library import Library


class Entry(msgspec.Struct):
    text: str
    url: str
    options: ResultConstructorKwargs = msgspec.field(default_factory=dict)  # type: ignore
    ctx_menu: list[Entry] = msgspec.field(default_factory=list)

    def get_result_kwargs(self, lib: Library, score: int) -> ResultConstructorKwargs:
        kwargs = self.options.copy()
        kwargs["title"] = self.text
        if "icon" not in kwargs and lib.icon:
            kwargs["icon"] = lib.icon
        kwargs["score"] = score

        return kwargs
