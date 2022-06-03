import pytest

from ...other_stuff import test_engine, TestEngine, SimpleModel


async def test_add_one_simple_model(test_engine: TestEngine):
    async with test_engine:

        collection = test_engine[SimpleModel]

        collection.add(SimpleModel(0, "A", False, 0.0))

        changes_made = await collection.save_changes_async()

        assert changes_made == 1

        assert await collection.count_async() == 1


async def test_add_range_simple_model(test_engine: TestEngine):
    async with test_engine:

        collection = test_engine[SimpleModel]

        collection.add_range(
            SimpleModel(0, "A", False, 0.0),
            SimpleModel(0, "A", False, 0.0),
            SimpleModel(0, "A", False, 0.0),
        )

        changes_made = await collection.save_changes_async()

        assert changes_made == 3

        assert await collection.count_async() == 3


async def test_add_range_simple_model_advanced_1(test_engine: TestEngine):
    async with test_engine:

        collection = test_engine[SimpleModel]

        collection.add_range(
            SimpleModel(0, "A", False, 0.0),
            SimpleModel(0, "A", False, 0.0),
            SimpleModel(0, "A", False, 0.0),
        )

        changes_made = await collection.save_changes_async()

        assert changes_made == 3

        assert await collection.count_async() == 3

        async with collection.get_queryable() as models:

            assert await models.all_async(lambda m: m.string_field == "A")
            models.clear_filters()

            assert not await models.any_async(lambda x: x.boolean_field)
            models.clear_filters()

            assert await models.count_async(lambda m: m.float_field > 0.0) == 0
            models.clear_filters()

            assert await models.count_async(lambda m: m.float_field == 0.0) == 3
            models.clear_filters()
