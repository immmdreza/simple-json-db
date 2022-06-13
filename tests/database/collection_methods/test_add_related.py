# pylint: skip-file
# flake8: noqa

import time
from typing import Optional

from ...other_stuff import test_engine, TestEngine
from src.sjd import Engine, TEntity, properties as props


@props.auto_collect()
class InnerObject(TEntity):

    complex_object_id = props.reference()

    def __init__(self, very_secret_string: str) -> None:
        self.very_secret_string = very_secret_string


@props.auto_collect()
class ComplexObject(TEntity):

    inner_object = props.from_entity(InnerObject, "complex_object_id")

    def __init__(
        self, secret_string: str, inner_object: Optional[InnerObject] = None
    ) -> None:
        self.secret_string = secret_string
        self.inner_object = inner_object


async def test_add_1(test_engine: TestEngine):

    collection = test_engine[ComplexObject]

    collection.add(ComplexObject("secret_string", InnerObject("very_secret_string")))
    await collection.save_changes_async()

    async with collection.get_queryable() as items:

        the_only_item = await items.include(lambda i: i.inner_object).first_async()

        assert the_only_item.secret_string == "secret_string"
        assert the_only_item.inner_object
        assert the_only_item.inner_object.very_secret_string == "very_secret_string"

    await collection.purge_async()
    await test_engine[InnerObject].purge_async()


async def test_add_2(test_engine: TestEngine):

    collection = test_engine[ComplexObject]

    collection.add(ComplexObject("secret_string", InnerObject("very_secret_string")))
    await collection.save_changes_async()

    async with collection.get_queryable() as items:

        the_only_item = await items.include(lambda i: i.inner_object).first_async()

        assert the_only_item.secret_string == "secret_string"
        assert the_only_item.inner_object
        assert the_only_item.inner_object.very_secret_string == "very_secret_string"

        tracking_id = collection.resolve_tracked_entity_id(the_only_item)
        assert tracking_id
        assert tracking_id == the_only_item.inner_object.complex_object_id
    await collection.purge_async()
    await test_engine[InnerObject].purge_async()


async def test_delete_whole_reference(test_engine: TestEngine):
    class AppEngine(Engine):

        complexes = Engine.set(ComplexObject)
        inners = Engine.set(InnerObject)

        def __init__(self):
            super().__init__("__test_db__")

            self._configs.config_collection(
                lambda c: c.complexes,
                lambda c: c.config_property(
                    lambda p: p.inner_object, lambda p: p.delete_whole_reference()
                ),
            )

    engine = AppEngine()

    collection = engine.complexes

    collection.add(ComplexObject("secret_string", InnerObject("very_secret_string")))
    await collection.save_changes_async()

    async with collection.get_queryable() as items:

        the_only_item = await items.include(lambda i: i.inner_object).first_async()

        assert the_only_item.secret_string == "secret_string"
        assert the_only_item.inner_object
        assert the_only_item.inner_object.very_secret_string == "very_secret_string"

        tracking_id = collection.resolve_tracked_entity_id(the_only_item)
        assert tracking_id
        assert tracking_id == the_only_item.inner_object.complex_object_id

        collection.delete(the_only_item)
        await collection.save_changes_async()

    async with engine.inners.get_queryable() as inner_items:

        first = await inner_items.first_or_default_async()

        assert first == None

    await collection.purge_async()
    await engine.inners.purge_async()


async def test_delete_reference_property(test_engine: TestEngine):
    class AppEngine(Engine):

        complexes = Engine.set(ComplexObject)
        inners = Engine.set(InnerObject)

        def __init__(self):
            super().__init__("__test_db__")

            self._configs.config_collection(
                lambda c: c.complexes,
                lambda c: c.config_property(
                    lambda p: p.inner_object, lambda p: p.delete_reference_prop()
                ),
            )

    engine = AppEngine()

    collection = engine.complexes

    collection.add(ComplexObject("secret_string", InnerObject("very_secret_string")))
    await collection.save_changes_async()

    async with collection.get_queryable() as items:

        the_only_item = await items.include(lambda i: i.inner_object).first_async()

        assert the_only_item.secret_string == "secret_string"
        assert the_only_item.inner_object
        assert the_only_item.inner_object.very_secret_string == "very_secret_string"

        tracking_id = collection.resolve_tracked_entity_id(the_only_item)
        assert tracking_id
        assert tracking_id == the_only_item.inner_object.complex_object_id

        collection.delete(the_only_item)
        await collection.save_changes_async()

    async with engine.inners.get_queryable() as inner_items:

        first = await inner_items.first_or_default_async()

        assert first is not None
        assert first.complex_object_id == None

    await collection.purge_async()
    await engine.inners.purge_async()
