from typing import ClassVar
import pytest

from ..test_engine import test_engine, TestEngine  # type: ignore
from src.sjd import TEntity, properties as props


class SimpleModel(TEntity):
    __json_init__: ClassVar[bool] = True

    # @props.string("name") # ? Feature

    numeric_field = props.IntProperty()
    string_field = props.StrProperty()
    boolean_field = props.BoolProperty()
    float_field = props.FloatProperty()

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


@pytest.fixture
def my_engine(test_engine: TestEngine) -> TestEngine:
    test_engine.register_collection(SimpleModel)
    return test_engine


@pytest.mark.asyncio
async def test_add_data(my_engine: TestEngine):
    with my_engine:
        collection = my_engine.get_collection(SimpleModel)
        assert collection

        # TODO add count() to the collection.

        # TODO return added entity from add().
        await collection.add(SimpleModel(1, "test", True, 1.0))

        added = await collection.as_queryable.first()

        assert added.numeric_field == 1
        assert added.string_field == "test"
        assert added.boolean_field is True
        assert added.float_field == 1.0
