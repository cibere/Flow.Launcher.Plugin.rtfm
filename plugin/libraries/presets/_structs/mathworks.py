import msgspec


def _strip_blanks(data: list[str]):
    for item in data:
        if not item.strip():
            data.remove(item)


class Suggestion(msgspec.Struct):
    title: list[str]
    summary: list[str]
    product: str
    shortName: str
    pageId: str
    path: str
    type: str

    @property
    def label(self) -> str:
        return f"{''.join(self.title)} - {''.join(self.summary)}"


class Page(msgspec.Struct):
    header: str
    type: str
    more: int
    q: str
    suggestions: list[Suggestion]


class Response(msgspec.Struct):
    searchtext: str
    pages: list[Page]
