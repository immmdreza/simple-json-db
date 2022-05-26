import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    Callable,
    Coroutine,
    Generic,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    final,
    overload,
)

import ijson  # type: ignore
import aiofiles

from ..entity import TEntity, TProperty
from ..query import AsyncQueryable
from ..serialization import deserialize, serialize
from ..serialization._shared import T
from ..entity.properties import (
    VirtualComplexProperty,
    ReferenceProperty,
    VirtualListProperty,
)

if TYPE_CHECKING:
    from ._engine import Engine


_T = TypeVar("_T")


class _TempCollectionFile(AsyncIterable[str]):
    def __init__(self, file_path: Path, mode: Any = "r") -> None:
        self._file_path = file_path
        self._mode = mode
        self._file = None

    async def __aiter__(self):
        async with aiofiles.open(self._file_path, self._mode) as tmp_file:
            self._file = tmp_file
            async for line in tmp_file:
                yield line

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self._file is not None:
            await self._file.close()
        os.remove(self._file_path)


class Collection(Generic[T]):
    """A collection of an specified entity type. Acts like a table."""

    def __init__(
        self, engine: "Engine", entity_type: type[T], name: Optional[str] = None, /
    ) -> None:
        """Create a new collection.

        Args:
            engine (`Engine`): The engine to use.
            entity_type (`type`): The type of the entity.
            name (`str`, optional): The name of the collection. Defaults to name of entity_type.
        """

        # if engine is None or not isinstance(engine, Engine):  # type: ignore
        #     raise ValueError("engine must be an instance of Engine")
        self._engine = engine

        if entity_type is None or not isinstance(entity_type, type):  # type: ignore
            raise ValueError("entity_type must be a type")

        self._name = name or entity_type.__name__

        if not issubclass(entity_type, TEntity):  # type: ignore
            raise TypeError(
                f"The entity_type must be a subclass of {TEntity.__name__}."
            )

        self._entity_type: type[T] = entity_type  # type: ignore
        self._instance_numbers = 1
        self._main_file_lock = asyncio.Lock()

    @final
    @property
    def name(self) -> str:
        """Get the name of the collection."""
        return self._name

    @final
    @property
    def entity_type(self) -> type[T]:
        """Get the type of the entity."""
        return self._entity_type

    @final
    @property
    def as_queryable(self) -> AsyncQueryable[T]:
        """Get a queryable object for this collection."""
        return AsyncQueryable(self)

    @staticmethod
    def _check_by_id(line_of: str, __id: str) -> bool:
        return line_of[10:46] == __id

    @final
    def _collection_path_builder(self):
        return self._engine.get_base_path(self) / self._name

    @final
    def _collection_tmp_path_builder(self, instance_number: int):
        return self._engine.get_base_path(self) / f"__{self._name}_{instance_number}__"

    @final
    def _collection_exists(self) -> bool:
        collection_path = self._collection_path_builder()
        return collection_path.exists()

    @final
    async def _create_collection(self):
        collection_path = self._collection_path_builder()
        async with aiofiles.open(collection_path, "w") as f:
            await f.write("")

    @final
    async def _tmp_collection_file(self, mode: Any = "r"):
        tmp_path = self._collection_tmp_path_builder(self._instance_numbers)
        main_file = self._collection_path_builder()

        async with self._main_file_lock:
            shutil.copyfile(main_file.absolute(), tmp_path.absolute())

        self._instance_numbers += 1
        async with _TempCollectionFile(tmp_path, mode) as tmp_file:
            async for line in tmp_file:
                yield line
        self._instance_numbers -= 1

    @final
    async def __aiter__(self):
        async for line in self._tmp_collection_file():
            data = deserialize(self._entity_type, json.loads(line))
            if data is not None:
                yield data

    @final
    async def _ensure_collection_exists(self) -> None:
        async with self._main_file_lock:
            if not self._collection_exists():
                await self._create_collection()

    @final
    async def _manage_referral_properties(self, entity: TEntity):
        for prop in entity.get_properties():
            if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                values: TEntity | list[TEntity] = getattr(entity, prop.actual_name)

                if not isinstance(values, list):
                    values = [values]

                for value in values:
                    virtual_reference_found = False
                    for virt_prop in value.get_properties():
                        if isinstance(virt_prop, ReferenceProperty):
                            if virt_prop.actual_name == prop.refers_to:
                                virtual_reference_found = True
                                setattr(value, virt_prop.actual_name, entity.id)

                                # get a collection for reference type
                                col = self._engine.get_collection(prop.type_of_entity)  # type: ignore
                                if col is None:
                                    raise ValueError(
                                        f"No collection for referenced type {prop.type_of_entity} found"  # type: ignore
                                    )

                                await col.add(value)  # type: ignore
                                delattr(entity, prop.actual_name)
                    if not virtual_reference_found:
                        raise TypeError(
                            f"No ReferenceProperty found for {prop.refers_to}."
                        )

    @final
    async def _add_to_file_async(self, entity: T) -> None:

        if not isinstance(entity, self._entity_type):
            raise TypeError(f"The entity must be of type {self._entity_type.__name__}.")

        if isinstance(entity, TEntity):
            # Check for reference properties
            await self._manage_referral_properties(entity)
        else:
            raise TypeError("Entity should be an instance of TEntity.")

        async with self._main_file_lock:
            async with aiofiles.open(self._collection_path_builder(), "a") as f:
                data = json.dumps(serialize(entity))
                await f.write(data + "\n")

    @final
    async def _add_many_to_file_async(self, *entities: T) -> None:

        for e in entities:
            if not isinstance(e, self._entity_type):
                raise TypeError(
                    f"All entities must be of type {self._entity_type.__name__}."
                )

            if isinstance(e, TEntity):
                # Check for reference properties
                await self._manage_referral_properties(e)
            else:
                raise TypeError("Entity should be an instance of TEntity.")

        # TODO Add reference stuff here too

        async with self._main_file_lock:
            async with aiofiles.open(self._collection_path_builder(), "a") as f:
                for entity in entities:
                    data = json.dumps(serialize(entity))
                    await f.write(data + "\n")

    @final
    async def _update_async(
        self,
        query: Callable[[type[T]], bool],
        update: Optional[Callable[[T], None]] = None,
        one: bool = True,
    ) -> None:

        if query is None:
            raise ValueError("query must not be None")

        async with self._main_file_lock:
            file_path = self._collection_path_builder()
            tmp_path = self._collection_tmp_path_builder(0)
            modified = False
            async with aiofiles.open(file_path, "r") as f:
                async with aiofiles.open(tmp_path, "w") as tmp_f:
                    async for line in f:

                        if one and modified:
                            await tmp_f.write(line)
                            continue

                        current_data = deserialize(self._entity_type, json.loads(line))
                        if current_data is not None and query(current_data):  # type: ignore
                            if update is not None:
                                update(current_data)
                                data = json.dumps(serialize(current_data))
                                await tmp_f.write(data + "\n")
                            else:
                                await tmp_f.write("")
                            modified = True
                        else:
                            await tmp_f.write(line)

            if modified:
                os.remove(file_path.absolute())
                os.rename(tmp_path.absolute(), file_path.absolute())
            else:
                os.remove(tmp_path.absolute())

    @final
    async def _update_entity_async(self, entity: T, delete: bool = False) -> None:

        if not isinstance(entity, self._entity_type):
            raise TypeError(f"The entity must be of type {self._entity_type.__name__}.")

        async with self._main_file_lock:
            file_path = self._collection_path_builder()
            tmp_path = self._collection_tmp_path_builder(0)
            modified = False
            async with aiofiles.open(file_path, "r") as f:
                async with aiofiles.open(tmp_path, "w") as tmp_f:
                    async for line in f:

                        if modified:
                            await tmp_f.write(line)
                            continue

                        if Collection._check_by_id(line, entity.id):  # type: ignore
                            if delete:
                                await tmp_f.write("")
                            else:
                                data = json.dumps(serialize(entity))
                                await tmp_f.write(data + "\n")
                            modified = True
                        else:
                            await tmp_f.write(line)

            if modified:
                os.remove(file_path.absolute())
                os.rename(tmp_path.absolute(), file_path.absolute())
            else:
                os.remove(tmp_path.absolute())

    async def get(self, __id: str):
        """Get an entity by its id.

        Args:
            __id (`str`): The id of the entity.
        """

        async for line in self._tmp_collection_file():
            if Collection._check_by_id(line, __id):
                data = deserialize(self._entity_type, json.loads(line))
                return data
        return None

    @overload
    def iter_by_prop_value(
        self, selector: str, __value: Any, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): The name of the property
            (You can use something like `item.name`, but The item should be an EmbedEntity).
            __value (`Any`): The value of the property.
        """
        ...

    @overload
    def iter_by_prop_value(
        self, selector: Callable[[type[T]], Any], __value: Any, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): A function to select a property (Can't allow nested props).
            __value (`Any`): The value of the property.
        """
        ...

    async def iter_by_prop_value(
        self, selector: str | Callable[[type[T]], Any], __value: Any, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): The name of the property
            (You can use something like `item.name`, but The item should be an EmbedEntity).
            __value (`Any`): The value of the property.
        """

        if callable(selector):
            prop = selector(self._entity_type)
            if isinstance(prop, TProperty):
                selector = prop.json_property_name or prop.actual_name

        async for line in self._tmp_collection_file("rb"):
            for item in ijson.items(line, selector):
                if item == __value:
                    data = deserialize(self._entity_type, json.loads(line))
                    if data is not None:
                        yield data
                    break

    @overload
    def get_first(
        self, selector: str, __value: Any
    ) -> Coroutine[Any, Any, Optional[T]]:
        """Get the first entity that has a certain property value."""
        ...

    @overload
    def get_first(
        self, selector: Callable[[type[T]], Any], __value: Any
    ) -> Coroutine[Any, Any, Optional[T]]:
        """Get the first entity that has a certain property value."""
        ...

    async def get_first(
        self, selector: str | Callable[[type[T]], Any], __value: Any
    ) -> Optional[T]:
        """Get the first entity that has a certain property value."""

        async for item in self.iter_by_prop_value(selector, __value):
            return item
        return None

    async def drop(self) -> None:
        """Drop the collection."""

        async with self._main_file_lock:
            if self._collection_exists():
                os.remove(self._collection_path_builder().absolute())

    async def update(self, entity: T) -> None:
        """Update an entity in the collection.

        Args:
            entity (`T`): The entity to update.
        """

        await self._update_entity_async(entity)

    async def delete(self, entity: T) -> None:
        """Delete an entity from the collection.

        Args:
            entity (`T`): The entity to delete.
        """

        await self._update_entity_async(entity, delete=True)

    async def update_one(
        self, query: Callable[[type[T]], bool], update: Callable[[T], None]
    ) -> None:
        """Update the first entity that matches the query.

        Args:
            query (`Query[T]`): The query to match.
            entity (`T`): The entity to update.
        """

        await self._ensure_collection_exists()
        await self._update_async(query, update, one=True)

    async def update_many(
        self, query: Callable[[type[T]], bool], update: Callable[[T], None]
    ) -> None:
        """Update all entities that match the query.

        Args:
            query (`Query[T]`): The query to match.
            entity (`T`): The entity to update.
        """

        await self._ensure_collection_exists()
        await self._update_async(query, update, one=False)

    async def delete_one(self, query: Callable[[type[T]], bool]) -> None:
        """Delete the first entity that matches the query.

        Args:
            query (`Query[T]`): The query to match.
        """

        await self._ensure_collection_exists()
        await self._update_async(query, one=True)

    async def delete_many(self, query: Callable[[type[T]], bool]) -> None:
        """Delete all entities that match the query.

        Args:
            query (`Query[T]`): The query to match.
        """

        await self._ensure_collection_exists()
        await self._update_async(query, one=False)

    async def add(self, entity: T) -> None:
        """Add an entity to the collection.

        Args:
            entity (`T`): The entity to add to the collection.
        """

        await self._ensure_collection_exists()
        await self._add_to_file_async(entity)

    async def add_many(self, *entities: T) -> None:
        """Add multiple entities to the collection."""

        await self._ensure_collection_exists()
        await self._add_many_to_file_async(*entities)

    async def load_virtual_props(self, entity: T, *props: str):
        """Load all virtual properties based on references."""

        if isinstance(entity, TEntity):
            for prop in entity.get_properties():

                if props and prop.actual_name not in props:
                    continue

                except_one = False
                if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                    except_one = isinstance(prop, VirtualComplexProperty)
                    # get a collection for reference type
                    col = self._engine.get_collection(prop.type_of_entity)  # type: ignore
                    if col is None:
                        raise ValueError(
                            f"No collection for referenced type {prop.type_of_entity} found"  # type: ignore
                        )

                    # TODO: Is this performance wise ?
                    results: list[Any] = []
                    async for item in col.iter_by_prop_value(prop.refers_to, entity.id):
                        if except_one:
                            setattr(entity, prop.actual_name, item)
                            return
                        else:
                            results.append(item)
                    setattr(entity, prop.actual_name, results)
        else:
            raise TypeError("Entity should be an instance of TEntity.")

    async def iter_referenced_by(
        self,
        entity: T,
        selector: Callable[[type[T]], Optional[_T] | Optional[list[_T]]],
    ) -> AsyncIterable[_T]:
        """Iterate over all virtual objects of an property.

        Args:
            entity (`T`): The reference entity.
            selector (`Callable[[type[T]], _T | list[_T]]`): The property selector should select a virtual prop.
        """

        if isinstance(entity, TEntity):
            prop = selector(self._entity_type)
            if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                # get a collection for reference type
                col = self._engine.get_collection(prop.type_of_entity)
                if col is None:
                    raise ValueError(
                        f"No collection for referenced type {prop.type_of_entity} found"
                    )
                async for item in col.iter_by_prop_value(prop.refers_to, entity.id):
                    yield item  # type: ignore
        else:
            raise TypeError("Entity should be an instance of TEntity.")

    def purge(self):
        """Purge the collection."""
        os.remove(self._collection_path_builder().absolute())
