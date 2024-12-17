import logging
import tempfile
from typing import TYPE_CHECKING, Any

import favicon
import requests
import yarl

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


def url_to_bytes(url: str, format: str):
    res = requests.get(url)
    if format == "svg":
        with wand.image.Image() as image:
            with wand.color.Color("transparent") as background_color:
                wand_lib.MagickSetBackgroundColor(image.wand, background_color.resource)
            image.read(blob=res.content, format="svg", height=500, width=500)
            return image.make_blob("png32")
    return res.content


def get_icon(key: str, url: str) -> str | None:
    if wand_installed is False:
        log.info("Wand not installed, attempting to build google URL.")
        u = yarl.URL(url)
        domain = u.host
        if domain:
            return str(
                yarl.URL.build(
                    scheme="https",
                    host="www.google.com",
                    path="/s2/favicons",
                    query={"domain_url": domain},
                )
            )
        log.error("Google URL could not be built")
    else:
        raw_icons = favicon.get(url)
        log.info(f"Found icons for {key} @ {url}: {raw_icons!r}")
        for icon in raw_icons:
            icon_url = icon[0]
            format = icon[3]

            file = url_to_bytes(icon_url, format)
            assert file

            with tempfile.NamedTemporaryFile(
                delete_on_close=False, suffix=".png", delete=False
            ) as f:
                f.write(file)
                log.info(f"Saved icon for {key} at {f.name}")
                return f.name
