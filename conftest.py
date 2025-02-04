import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--dump", action="store_true")
