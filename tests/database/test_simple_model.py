# pylint: skip-file
# flake8: noqa


import pytest

from ..other_stuff import test_engine, TestEngine, SimpleModel  # type: ignore


@pytest.fixture
def my_engine(test_engine: TestEngine) -> TestEngine:
    test_engine["simpleModels"] = SimpleModel
    return test_engine


async def test_add_data(my_engine: TestEngine):
    collection = my_engine[SimpleModel]
    assert collection

    collection.add(SimpleModel(1, "test", True, 1.0))

    await collection.save_changes_async()

    async with collection.get_queryable() as iter_ctx:
        added = await iter_ctx.first_async()

        assert added.numeric_field == 1
        assert added.string_field == "test"
        assert added.boolean_field is True
        assert added.float_field == 1.0
    await collection.purge_async()


async def test_update_data(my_engine: TestEngine):
    collection = my_engine.get_collection(SimpleModel)
    assert collection

    e = collection.add(SimpleModel(1, "test", True, 1.0))
    await collection.save_changes_async()

    added = await collection.get_async(e.key)

    assert added

    added.boolean_field = False
    await collection.save_changes_async()

    new_added = await collection.get_async(e.key)

    assert new_added
    assert new_added.boolean_field is False
    await collection.purge_async()
