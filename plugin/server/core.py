from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web

from ..libraries import doc_types, preset_docs

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from ..plugin import RtfmPlugin

log = logging.getLogger("webserver")

DATA_JS_TEMPLATE = """
const presetOptions = {presets};
const docTypes = {doctypes};
const libraries = {libraries}
"""

no_cache_headers = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Expires": "0",
    "Pragma": "no-cache",
}


def build_app(
    write_settings: Callable[[list[dict[str, str]]], Awaitable[None]],
    plugin: RtfmPlugin,
) -> web.Application:
    routes = web.RouteTableDef()

    @routes.put("/api/save_settings")
    async def save_settings(request: web.Request):
        content = await request.json()
        log.info(f"Writiting new settings: {content}")
        await write_settings(content)
        asyncio.create_task(plugin.build_rtfm_lookup_tables())
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

    @routes.put("/api/set_static_port")
    async def set_static_port(request: web.Request):
        content = await request.json()
        log.info(f"Writiting new static port: {content}")
        port = content.get("port")
        if port:
            plugin.static_port = port
            return web.json_response({"success": True})
        return web.json_response({"success": False})

    @routes.get("/")
    @aiohttp_jinja2.template("template.html")
    async def index(request: web.Request):
        data = {
            "libs": plugin.libraries.values(),
            "main_kw": plugin.main_kw,
            "static_port": plugin.static_port,
        }
        log.info(f"Sending data: {data}")
        return data

    @routes.get("/style.css")
    async def style(request: web.Request):
        return web.FileResponse(
            os.path.join(os.path.dirname(__file__), "style.css"),
            headers=no_cache_headers,
        )

    @routes.get("/script.js")
    async def script(request: web.Request):
        return web.FileResponse(
            os.path.join(os.path.dirname(__file__), "script.js"),
            headers=no_cache_headers,
        )

    @routes.get("/data.js")
    async def get_data(request: web.Request):
        presets = [pre.classname for pre in preset_docs]
        doctypes = [typ.classname for typ in doc_types] + ["auto"]
        libs = [lib.to_dict() for lib in plugin.libraries.values()]

        return web.Response(
            body=DATA_JS_TEMPLATE.format(
                presets=presets, doctypes=doctypes, libraries=json.dumps(libs)
            ),
            headers=no_cache_headers,
        )

    @routes.get("/local-docs/{name}/{path:[^{}]+}")
    async def get_local_doc_path(request: web.Request):
        name = request.match_info["name"]
        path = request.match_info["path"].strip("/") or "index.html"

        try:
            lib = plugin.libraries[name]
        except KeyError:
            return web.Response(body="Library not found")
        assert lib.path
        page = os.path.join(lib.path, path)
        log.info(f"Returning file: {page!r}")
        return web.FileResponse(page)

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    app.add_routes(routes)
    return app


async def start_runner(app: web.Application, host: str, port: int):
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)

    try:
        await site.start()
    except OSError as e:
        # check port/host is already in use and if port is a custom static port
        if e.errno == 10048 and port != 0:
            log.warning(
                "Static port is taken, restarting webserver with port 0", exc_info=e
            )
            return await start_runner(app, host, 0)
        raise

    socket_info: tuple[str, int] = site._server.sockets[0].getsockname()  # type: ignore
    return socket_info[1]


async def run_app(
    write_settings: Callable[[list[dict[str, str]]], Awaitable[None]],
    plugin: RtfmPlugin,
    *,
    run_forever: bool = True,
) -> None:
    app = build_app(write_settings, plugin)
    port = await start_runner(app, "localhost", plugin.static_port)

    if plugin.static_port != 0 and port != plugin.static_port:
        await plugin.api.show_notification(
            "rtfm",
            f"Your chosen static port ({plugin.static_port}) was already in use so webserver started on port {port}",
        )

    plugin.webserver_port = port
    plugin.webserver_ready_future.set_result(None)

    log.info(f"Started webserver on port {port}")

    while run_forever:
        await asyncio.sleep(10000)
