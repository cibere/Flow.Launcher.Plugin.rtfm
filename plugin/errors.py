class PromptRequired(Exception):
    def __init__(self, text: str, options: list[str], slug: str) -> None:
        self.text = text
        self.options = options
        self.slug = slug

        super().__init__(text)

    @property
    def message(self) -> str:
        return f"{self.text}\n" + "\n".join(
            [f"{num + 1}) {opt}" for num, opt in enumerate(self.options)]
        )
