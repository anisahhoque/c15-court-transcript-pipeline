import pytest
from main import greet


def test_greet():
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"
    assert greet("") == "Hello, !"


if __name__ == "__main__":
    pytest.main()
