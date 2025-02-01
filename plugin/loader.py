from __future__ import annotations

import importlib.util
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

log = getLogger(__name__)

MISSING: Any = object()


class PythonFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def typename(self) -> str:
        return self.path.name.removesuffix(".py")

    def run(self) -> Any:
        spec = importlib.util.spec_from_file_location(self.typename, self.path)
        assert spec
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        return module


class FileLoader:
    def __init__(self, loc: Path | str, *, exclude: list[str] = MISSING) -> None:
        self.exclusions = [] if exclude is MISSING else exclude

        if isinstance(loc, str):
            loc = Path(loc)
        if not loc.is_dir():
            self.exclusions.append(loc.name)
            loc = loc.parent

        self.dir = loc

    def __iter__(self) -> Iterator[PythonFile]:
        for file in self.dir.glob("*.py"):
            yield PythonFile(file)

    def getattrs(self, attr: str) -> Iterator[Any]:
        for file in self:
            if file.name in self.exclusions:
                continue

            item = getattr(file.run(), attr, MISSING)
            if item is not MISSING:
                yield item


def load_item_or_items(attr: str, fp: str) -> Iterator[Any]:
    loader = FileLoader(fp)
    for item in loader.getattrs(attr):
        if isinstance(item, tuple):
            yield from item
        else:
            yield item
