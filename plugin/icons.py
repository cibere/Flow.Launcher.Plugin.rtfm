import logging
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests
from favicon import favicon
from yarl import URL

if TYPE_CHECKING:
    import wand.color
    import wand.image
    from wand.api import library as wand_lib

    wand_installed: bool
else:
    try:
        import wand.color
        import wand.image
        from wand.api import library as wand_lib
    except ImportError:
        wand_installed = False
        wand: Any = None
        wand_lib: Any = None
    else:
        wand_installed = True

log = logging.getLogger(__name__)


def url_to_bytes(url: str, format: str) -> bytes | None:
    res = requests.get(url, timeout=5)

    if format != "svg":
        return res.content

    if wand_installed is False:
        return

    with wand.image.Image() as image:
        with wand.color.Color("transparent") as background_color:
            wand_lib.MagickSetBackgroundColor(image.wand, background_color.resource)
        image.read(blob=res.content, format="svg", height=500, width=500)
        return image.make_blob("png32")


def get_favicon(url: Path | URL) -> Iterable[favicon.Icon]:
    if isinstance(url, Path):
        return favicon.tags(str(url), url.read_bytes())
    return favicon.get(str(url))


def build_google_favicon_url(domain: str) -> str:
    return str(
        URL.build(
            scheme="https",
            host="www.google.com",
            path="/s2/favicons",
            query={"domain_url": domain},
        )
    )


def get_local_icon(key: str, path: Path) -> str | None:
    raw_icons = get_favicon(path)
    log.debug("Found icons for %s @ %r: %r", key, path, raw_icons)
    for icon in raw_icons:
        icon_url = icon[0]

        fp = path.parent / icon_url
        log.debug("Chosen icon for %s is %r", key, fp)
        return str(fp)


def handle_raw_icon(file: bytes | None, url: URL) -> str | None:
    if file is None:
        domain = url.host
        if domain is None:
            return

        return build_google_favicon_url(domain)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(file)
        return f.name


def get_online_icon(key: str, url: URL) -> str | None:
    if url.parts[-1].endswith(
        (
            ".ico",
            ".png",
        )
    ):
        icon = requests.get(str(url), timeout=5)
        return handle_raw_icon(icon.content, url)

    raw_icons = get_favicon(url)
    log.debug("Found icons for %s @ %s: %r", key, url, raw_icons)
    for icon in raw_icons:
        icon_url = icon[0]
        format = icon[3]

        file = url_to_bytes(icon_url, format)
        filename = handle_raw_icon(file, url)
        log.debug("Saved icon for %s at %s", key, filename)
        return filename


def get_icon(key: str, loc: URL | str | Path) -> str | None:
    if isinstance(loc, str):
        loc = URL(loc)
    if isinstance(loc, URL):
        return get_online_icon(key, loc)
    if isinstance(loc, Path):
        return get_local_icon(key, loc)
    raise ValueError(f"Unknown loc type {type(loc)!r}")
