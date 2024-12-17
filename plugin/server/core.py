from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING, Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web

if TYPE_CHECKING:
    from ..plugin import RtfmPlugin

log = logging.getLogger("webserver")


async def run_app(
    write_settings: Callable[[list[dict[str, str]]], None],
    plugin: RtfmPlugin,
    *,
    run_forever: bool = True,
):
    routes = web.RouteTableDef()
    is_alive = asyncio.Future()

    @routes.put("/api/save_settings")
    async def save_settings(request: web.Request):
        content = await request.json()
        log.info(f"Writiting new settings: {content}")
        write_settings(content)
        log.info(f"Reloading cache")
        await plugin.build_rtfm_lookup_table()
        log.info("Cache reloaded")
        return web.json_response({"success": True})

    @routes.put("/api/set_main_kw")
    async def set_main_kw(request: web.Request):
        content = await request.json()
        log.info(f"Writiting new settings kw: {content}")
        kw = content.get("keyword")
        if kw:
            plugin.main_kw = kw
            asyncio.create_task(plugin.ensure_keywords())
            return web.json_response({"success": True})
        return web.json_response({"success": False})

    @routes.get("/")
    @aiohttp_jinja2.template("template.html")
    async def index(request: web.Request):
        data = {
            "libs": [(key, value) for key, value in plugin.libraries.items()],
            "main_kw": plugin.main_kw,
        }
        log.info(f"Sending data: {data}")
        return data

    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", 2907)
    await site.start()

    if run_forever:
        await is_alive
