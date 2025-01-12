from __future__ import annotations

import asyncio
import base64
import logging
from typing import TYPE_CHECKING

import msgspec
from aiohttp import web

from ..libraries.library import PartialLibrary
from .payloads.get_library import GetLibraryPayload, GetLibraryResponse
from .payloads.settings import (
    ExportSettingsResponse,
    ImportSettingsRequest,
    PluginSettings,
)

if TYPE_CHECKING:
    from ..plugin import RtfmPlugin

log = logging.getLogger("webserver.api")


no_cache_headers = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Expires": "0",
    "Pragma": "no-cache",
}


def build_api(
    routes: web.RouteTableDef,
    plugin: RtfmPlugin,
):
    @routes.put("/api/settings")
    async def save_settings(request: web.Request):
        try:
            data = PluginSettings.decode(await request.content.read())
        except msgspec.DecodeError:
            return web.json_response({"success": False})

        plugin.static_port = data.port
        plugin.main_kw = data.keyword

        await plugin.update_libraries(data.libraries)
        asyncio.create_task(plugin.build_rtfm_lookup_tables())
        return web.json_response({"success": True}, headers=no_cache_headers)

    @routes.get("/api/settings")
    async def get_settings(request: web.Request):
        data = PluginSettings(
            port=plugin.static_port,
            keyword=plugin.main_kw,
            libraries=[lib.to_partial() for lib in plugin.libraries.values()],
        )

        return web.Response(body=data.encode(), headers=no_cache_headers)

    @routes.post("/api/get_library")
    async def get_library(request: web.Request):
        try:
            data = GetLibraryPayload.decode(await request.read())
        except msgspec.DecodeError:
            return web.json_response(
                {"success": False, "message": "Invalid Data Received"}
            )
        lib = await plugin.get_library_from_url(data.name, data.url)
        if lib is None:
            return web.json_response(
                {"success": False, "message": "Could not index site"}
            )

        log.info(f"{lib=}")

        response = GetLibraryResponse(lib.to_partial())
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.get("/api/export_settings")
    async def export_settings(request: web.Request):
        obj = PluginSettings(
            plugin.static_port,
            plugin.main_kw,
            [
                PartialLibrary(
                    lib.name,
                    lib.typename,
                    str(lib.loc),
                    lib.use_cache,
                    lib.is_api,
                )
                for lib in plugin.libraries.values()
            ],
        )
        response = ExportSettingsResponse(base64.b64encode(obj.encode()).decode())
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.post("/api/import_settings")
    async def import_settings(request: web.Request):
        try:
            data = ImportSettingsRequest.decode(await request.read())
            settings = PluginSettings.decode(base64.b64decode(data.data))
        except msgspec.DecodeError as e:
            log.exception("Error while import settings", exc_info=e)
            return web.json_response({"success": False})

        plugin.main_kw = settings.keyword
        plugin.static_port = settings.port
        await plugin.update_libraries(settings.libraries)
        asyncio.create_task(plugin.build_rtfm_lookup_tables())
        return web.json_response({"success": True}, headers=no_cache_headers)
