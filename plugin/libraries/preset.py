from typing import TYPE_CHECKING, ClassVar

from yarl import URL

from .library import Library


class PresetLibrary(Library):
    is_preset: ClassVar[bool] = True
    base_url: ClassVar[URL]
    typename: ClassVar[str] = "Preset"

    if TYPE_CHECKING:
        url: URL  # type: ignore
        loc: URL

    def __init_subclass__(
        cls, base_url: str | None = None, favicon_url: str | None = None
    ) -> None:
        if base_url:
            cls.base_url = URL(base_url)
        if favicon_url:
            cls.favicon_url = favicon_url
        return super().__init_subclass__()

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, URL(self.base_url), use_cache=use_cache)

    @classmethod
    def validate_url(cls, url: URL) -> bool:
        return url.host == cls.base_url.host
