# ruff: noqa: E402, F401

import sys
from pathlib import Path

root = Path(__file__).parent
prod_dir = root / "lib"
dev_dir = root / "venv" / "lib" / "site-packages"

lib_dir = prod_dir if prod_dir.exists() else dev_dir

sys.path.extend([root.as_posix(), lib_dir.as_posix()])

from flogin import Pip

from plugin.logs import Logs

logs = Logs()
logs.setup()

with Pip(lib_dir) as pip:
    pip.ensure_installed("msgspec==0.19.0", module="msgspec._core")

import asyncio

from plugin.plugin import RtfmPlugin
from rtfm_lookup import RtfmManager


async def main():
    async with RtfmManager(
        default_manual_options={"dont_cache_results": False}
    ) as rtfm:
        plugin = RtfmPlugin()
        plugin.rtfm = rtfm
        plugin.logs = logs

        plugin.load_settings()

        logs.update_debug(plugin.better_settings.debug_mode)
        asyncio.create_task(plugin.start_webserver())
        await plugin.start()


asyncio.run(main())
