# this is a preset used for testing, and does not actually relate to any documentation

from __future__ import annotations

from typing import TYPE_CHECKING

from plugin.libraries.entry import Entry
from plugin.libraries.preset import PresetLibrary

if TYPE_CHECKING:
    from aiohttp import ClientSession


class TestPreset(
    PresetLibrary, favicon_url="https://www.google.com", base_url="https://cibere.dev"
):
    async def build_cache(self, session: ClientSession, webserver_port: int) -> None:
        self.cache = {
            "foo": Entry(
                "foo",
                "https://www.google.com?q=test",
                options={"sub": "this is an abomination | hayaii"},
            ),
            "bar": Entry(
                "bar", "test", ctx_menu=[Entry("yes", "no"), Entry("no", "no")]
            ),
        }


preset = TestPreset
