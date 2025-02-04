from typing import TYPE_CHECKING, ClassVar

from yarl import URL

from .library import Library

__all__ = ("PresetLibrary",)


class PresetLibrary(Library):
    is_preset: ClassVar[bool] = True
    base_url: ClassVar[URL]
    typename: ClassVar[str] = "Preset"
    is_variant: ClassVar[bool] = False

    if TYPE_CHECKING:
        url: URL  # type: ignore
        loc: URL

    def __init_subclass__(
        cls,
        base_url: str | None = None,
        favicon_url: str | None = None,
        is_variant: bool | None = None,
    ) -> None:
        if base_url:
            cls.base_url = URL(base_url.rstrip("/"))
        if favicon_url:
            cls.favicon_url = favicon_url
        if is_variant is not None:
            cls.is_variant = is_variant
        return super().__init_subclass__()

    def __init__(self, name: str, *, use_cache: bool) -> None:
        super().__init__(name, URL(self.base_url), use_cache=use_cache)

    @classmethod
    def validate_url(cls, url: URL) -> bool:
        return (
            (url == cls.base_url) if cls.is_variant else (url.host == cls.base_url.host)
        )
