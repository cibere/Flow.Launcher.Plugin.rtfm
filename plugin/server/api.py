from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

import msgspec
from aiohttp import web

from .payloads.error import ErrorResponse
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
decoder = msgspec.json.Decoder()


def build_api(
    routes: web.RouteTableDef,
    plugin: RtfmPlugin,
):
    @routes.post("/api/settings")
    async def save_settings(request: web.Request):
        try:
            form_data = decoder.decode(await request.content.read())
            payload = PluginSettings.parse_form_data(form_data)
        except msgspec.DecodeError:
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        await payload.save(plugin)
        return web.json_response({"success": True}, headers=no_cache_headers)

    @routes.post("/api/get_library")
    async def get_library(request: web.Request):
        try:
            data = GetLibraryPayload.decode(await request.read())
        except msgspec.DecodeError:
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        lib = await plugin.get_library_from_url(data.name, data.url)
        if lib is None:
            return web.Response(
                body=ErrorResponse("Could not index site").encode(), status=400
            )

        response = GetLibraryResponse(lib.to_partial())
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.get("/api/export_settings")
    async def export_settings(request: web.Request):
        obj = PluginSettings.from_plugin(plugin)
        response = ExportSettingsResponse(base64.b64encode(obj.encode()).decode())
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.post("/api/import_settings")
    async def import_settings(request: web.Request):
        try:
            data = ImportSettingsRequest.decode(await request.read())
            settings = PluginSettings.decode(base64.b64decode(data.data))
        except msgspec.DecodeError as e:
            log.exception("Error while import settings", exc_info=e)
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        await settings.save(plugin)
        return web.json_response({"success": True}, headers=no_cache_headers)
