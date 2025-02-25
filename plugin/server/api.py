from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

import msgspec
from aiohttp import web

from ..settings import RtfmBetterSettings
from .payloads.error import ErrorResponse
from .payloads.get_manual import GetManualPayload, GetManualResponse
from .payloads.settings import (
    ExportSettingsResponse,
    ImportSettingsRequest,
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
            payload = RtfmBetterSettings.parse_form_data(form_data)
        except msgspec.DecodeError:
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        await payload.save(plugin)
        return web.json_response({"success": True}, headers=no_cache_headers)

    @routes.post("/api/get_manual")
    async def get_manual(request: web.Request):
        try:
            data = GetManualPayload.decode(await request.read())
        except msgspec.DecodeError:
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        man = await plugin.rtfm.get_manual(data.name, data.url, add=False)
        if man is None:
            return web.Response(
                body=ErrorResponse("Could not index site").encode(), status=400
            )

        response = GetManualResponse(man.to_partial())
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.get("/api/settings/export")
    async def export_settings(request: web.Request):
        response = ExportSettingsResponse(
            base64.b64encode(plugin.better_settings.encode()).decode()
        )
        return web.Response(body=response.encode(), headers=no_cache_headers)

    @routes.post("/api/settings/import")
    async def import_settings(request: web.Request):
        try:
            data = ImportSettingsRequest.decode(await request.read())
            settings = RtfmBetterSettings.decode(base64.b64decode(data.data))
        except msgspec.DecodeError as e:
            log.exception("Error while import settings", exc_info=e)
            return web.Response(
                body=ErrorResponse("Invalid Data Received").encode(), status=400
            )

        await settings.save(plugin)
        return web.json_response({"success": True}, headers=no_cache_headers)
