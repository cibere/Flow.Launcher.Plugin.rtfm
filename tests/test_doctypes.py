from collections.abc import Iterator

import pytest

from plugin.libraries.doctypes import fetch as fetch_doctypes
from plugin.libraries.library import Library

doctypes = fetch_doctypes()


@pytest.fixture(params=fetch_doctypes())
def doctype(request: pytest.FixtureRequest) -> Iterator[type[Library]]:
    return request.param


def test_doctype_classvars(doctype: type[Library]) -> None:
    assert doctype.is_preset is False
    assert doctype.typename
