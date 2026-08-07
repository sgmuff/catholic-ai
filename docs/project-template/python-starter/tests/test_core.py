import pytest

from example_package.core import greet


def test_greet_returns_greeting_for_name() -> None:
    assert greet("Ada") == "Hello, Ada."


def test_greet_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        greet("")
