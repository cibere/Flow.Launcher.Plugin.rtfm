from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

import aiohttp_jinja2
import jinja2
from aiohttp import web

from .api import build_api

if TYPE_CHECKING:
    from ..plugin import RtfmPlugin

log = logging.getLogger("webserver")

no_cache_headers = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Expires": "0",
    "Pragma": "no-cache",
}


def build_app(
    plugin: RtfmPlugin,
) -> web.Application:
    routes = web.RouteTableDef()
    build_api(routes, plugin)

    @routes.get("/")
    @aiohttp_jinja2.template("index.html")
    async def index(request: web.Request):
        return {"plugin": plugin}

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

    @routes.get("/favicon.ico")
    async def favicon(request: web.Request):
        return web.FileResponse(
            os.path.join("assets", "app.ico"),
            headers=no_cache_headers,
        )

    # @routes.get("/local-docs/{name}/{path:[^{}]+}")
    # async def get_local_doc_path(request: web.Request):
    #     name = request.match_info["name"]
    #     path = request.match_info["path"].strip("/") or "index.html"

    #     try:
    #         lib = plugin.libraries[name]
    #     except KeyError:
    #         return web.Response(body="Library not found", status=404)

    #     if lib.path is None:
    #         return web.Response(
    #             body="Library does not support local documentation", status=400
    #         )

    #     page = os.path.join(lib.path, path)
    #     log.debug("Returning file: %r", page)
    #     return web.FileResponse(page)

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    app.add_routes(routes)
    return app


async def start_runner(app: web.Application, host: str, port: int) -> int:
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
    plugin: RtfmPlugin,
    *,
    run_forever: bool = True,
) -> None:
    static_port = plugin.better_settings.static_port
    app = build_app(plugin)
    port = await start_runner(app, "localhost", static_port)

    if static_port != 0 and port != static_port:
        await plugin.api.show_notification(
            "rtfm",
            f"Your chosen static port ({static_port}) was already in use so webserver started on port {port}",
        )

    plugin.webserver_port = port
    plugin.webserver_ready_future.set_result(None)

    log.info("Started webserver on port %s", port)

    while run_forever:
        await asyncio.sleep(10000)
