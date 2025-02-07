import logging
import pathlib
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import aiohttp
import flogin
import msgspec
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
        path.write_bytes(
            msgspec.json.format(
                msgspec.json.encode(lib.cache, enc_hook=lambda obj: repr(obj))
            )
        )


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

    match = pytestconfig.getoption("--preset-domain")
    if match and str(match) not in str(cls.base_url.host):
        pytest.skip(f"Preset Domain match did not match preset url: {cls.base_url!r}")

    lib = cls("test", use_cache=True)

    yield lib

    _dump(lib, pytestconfig)


@pytest.fixture(params=api_presets)
def api_preset(
    request: pytest.FixtureRequest, pytestconfig: pytest.Config
) -> Iterator[PresetLibrary]:
    cls: type[PresetLibrary] = request.param

    match = pytestconfig.getoption("--preset-domain")
    if match and str(match) not in str(cls.base_url.host):
        pytest.skip(f"Preset Domain match did not match preset url: {cls.base_url!r}")

    lib = cls("test", use_cache=True)

    yield lib

    _dump(lib, pytestconfig)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession, Any]:
    async with aiohttp.ClientSession() as cs:
        yield cs


async def _test_preset(session: aiohttp.ClientSession, preset: PresetLibrary) -> None:
    assert preset.is_preset is True
    assert preset.typename == "Preset"
    assert preset.base_url

    assert preset.icon is None
    icon = await preset.fetch_icon()
    assert preset.icon is not None
    assert preset.icon == icon


@pytest.mark.asyncio
async def test_cached_preset(
    session: aiohttp.ClientSession, cached_preset: PresetLibrary
) -> None:
    await cached_preset.build_cache(session, 0)

    assert cached_preset.cache is not None
    assert cached_preset.cache != {}

    await _test_preset(session, cached_preset)


@pytest.mark.asyncio
async def test_api_preset(
    session: aiohttp.ClientSession, api_preset: PresetLibrary
) -> None:
    await api_preset.make_request(session, "foo")

    assert api_preset.cache is not None
    assert api_preset.use_cache is False

    await _test_preset(session, api_preset)
