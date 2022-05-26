from typing import Any

import pytest

from src.sjd import Engine


class TestEngine(Engine):
    def __init__(self):
        super().__init__("_test_engine_")

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self.purge()


@pytest.fixture(scope="session")
def test_engine() -> TestEngine:
    return TestEngine()
