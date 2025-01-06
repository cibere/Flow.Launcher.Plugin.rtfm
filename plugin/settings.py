from flogin import Settings


class RtfmSettings(Settings):
    libraries: dict[str, str] | None  # for legacy setting support
    main_kw: str | None
