import pytest

from ..test_engine import test_engine, TestEngine  # type: ignore
from src.sjd import TEntity, properties as props


@props.collect_props_from_init
class SimpleModel(TEntity):
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
    test_engine["simpleModels"] = SimpleModel
    return test_engine


async def test_add_data(my_engine: TestEngine):
    with my_engine:
        collection = my_engine[SimpleModel]
        assert collection

        await collection.add(SimpleModel(1, "test", True, 1.0))

        async with collection as iter_ctx:

            added = await iter_ctx.as_queryable.first()

            assert added.numeric_field == 1
            assert added.string_field == "test"
            assert added.boolean_field is True
            assert added.float_field == 1.0


async def test_update_data(my_engine: TestEngine):
    with my_engine:
        collection = my_engine.get_collection(SimpleModel)
        assert collection

        e = await collection.add(SimpleModel(1, "test", True, 1.0))

        added = await collection.get(e.id)

        assert added

        added.boolean_field = False

        await collection.update(added)

        new_added = await collection.get(added.id)

        assert new_added
        assert new_added.boolean_field is False
