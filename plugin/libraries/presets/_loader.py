from __future__ import annotations

import importlib.util
import os
import pathlib
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ..preset import PresetLibrary

log = getLogger(__name__)


def built_presets() -> Iterator[type[PresetLibrary]]:
    for file in pathlib.Path(os.path.dirname(__file__)).glob("*.py"):
        typename = file.name.removesuffix(".py")

        if file.name.startswith("_"):
            pass
        log.debug("Builting %r at %r", file.name, file)
        spec = importlib.util.spec_from_file_location(typename, file)
        assert spec
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)

        preset = getattr(module, "preset", None)
        if preset:
            yield (preset)
        presets = getattr(module, "presets", [])
        yield from presets
