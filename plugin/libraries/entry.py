from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import msgspec

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from flogin import Result, ResultConstructorKwargs

    from .library import Library


class CtxMenuFactory(Protocol):
    def __call__(self, entry: Entry) -> Sequence[Result] | Iterator[Result]: ...


class Entry(msgspec.Struct):
    text: str
    url: str
    options: ResultConstructorKwargs = msgspec.field(default_factory=dict)  # type: ignore
    ctx_menu_factory: CtxMenuFactory = msgspec.field(
        default_factory=lambda: lambda entry: []
    )

    def get_result_kwargs(self, lib: Library, score: int) -> ResultConstructorKwargs:
        kwargs = self.options.copy()
        kwargs["title"] = self.text
        if "icon" not in kwargs and lib.icon:
            kwargs["icon"] = lib.icon
        kwargs["score"] = score

        return kwargs
