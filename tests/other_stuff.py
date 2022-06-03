from typing import Any

import pytest

from src.sjd import Engine, TEntity, properties as props


@props.auto_collect()
class SimpleModel(TEntity):
    """Simple model with all types"""

    def __init__(
        self,
        numeric_field: int,
        string_field: str,
        boolean_field: bool,
        float_field: float,
    ):
        self.numeric_field = numeric_field
        self.string_field = string_field
        self.boolean_field = boolean_field
        self.float_field = float_field


class TestEngine(Engine):
    """Test engine"""

    def __init__(self):
        super().__init__("_test_engine_")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self.purge()


@pytest.fixture(scope="function")
def test_engine() -> TestEngine:
    """Test engine"""
    return TestEngine()
