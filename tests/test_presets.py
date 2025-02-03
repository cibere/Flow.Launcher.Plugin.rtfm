import json
import logging
import pathlib
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import aiohttp
import flogin
import pytest
import pytest_asyncio

from plugin.libraries.preset import PresetLibrary
from plugin.libraries.presets import fetch as fetch_presets

flogin.utils.setup_logging(handler=logging.StreamHandler())

tests_dir = pathlib.Path(__file__).parent
root = tests_dir.parent
caches_dir = root / "caches"
cached_presets: list[type[PresetLibrary]] = []
api_presets: list[type[PresetLibrary]] = []


def _dump(lib: PresetLibrary, pytestconfig: pytest.Config):
    if pytestconfig.getoption("dump"):
        caches_dir.mkdir(exist_ok=True)
        path = caches_dir / f"{lib.__class__.__name__}.json"
        with path.open("w") as f:
            json.dump(lib.cache, f, indent=4)


for PresetClass in fetch_presets():
    if PresetClass.is_api:
        api_presets.append(PresetClass)
    else:
        cached_presets.append(PresetClass)


@pytest.fixture(params=cached_presets)
def cached_preset(
    request: pytest.FixtureRequest, pytestconfig: pytest.Config
) -> Iterator[PresetLibrary]:
    cls: type[PresetLibrary] = request.param
    lib = cls("test", use_cache=True)

    yield lib

    _dump(lib, pytestconfig)


@pytest.fixture(params=api_presets)
def api_preset(
    request: pytest.FixtureRequest, pytestconfig: pytest.Config
) -> Iterator[PresetLibrary]:
    cls: type[PresetLibrary] = request.param
    lib = cls("test", use_cache=True)

    yield lib

    _dump(lib, pytestconfig)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession, Any]:
    async with aiohttp.ClientSession() as cs:
        yield cs


@pytest.mark.asyncio
async def test_cached_preset(
    session: aiohttp.ClientSession, cached_preset: PresetLibrary
) -> None:
    await cached_preset.build_cache(session, 0)

    assert cached_preset.cache is not None
    assert cached_preset.cache != {}


@pytest.mark.asyncio
async def test_api_preset(
    session: aiohttp.ClientSession, api_preset: PresetLibrary
) -> None:
    await api_preset.make_request(session, "foo")

    assert api_preset.cache is not None
