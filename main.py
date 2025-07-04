from pathlib import Path
from flogin import Pip
from rtfm_plugin.logs import Logs

logs = Logs()
logs.setup()

root = Path(__file__).parent
prod_dir = root / "lib"
dev_dir = root / "venv" / "lib" / "site-packages"

with Pip(prod_dir if prod_dir.exists() else dev_dir) as pip:
    pip.ensure_installed("msgspec==0.19.0", module="msgspec._core")

import asyncio

from rtfm_plugin.plugin import RtfmPlugin
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
