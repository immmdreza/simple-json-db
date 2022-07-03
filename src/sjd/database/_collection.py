from abc import ABC, abstractmethod
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
    cast,
    final,
    overload,
)
from uuid import uuid4

import ijson  # type: ignore
import aiofiles

from ._entity_tracker import _EntityTracker, TrackingMode
from ..entity._master_entity import (
    MasterEntityFactory,
    UuidMasterEntity,
    UuidMasterEntityFactory,
    MasterEntity,
    _TKey,
    _TMasterEntity,
)
from ..entity import TEntity, TProperty
from ..query._queryable import AbstractAsyncQueryable
from ..query._query_builder import QueryBuilder
from ..query._query_factory import QueryFactory
from ..serialization import deserialize, serialize
from ..serialization._shared import T
from ..entity.properties import (
    VirtualComplexProperty,
    ReferenceProperty,
    VirtualListProperty,
)

if TYPE_CHECKING:
    from ._engine import Engine
    from ._configuration import CollectionConfiguration


_T = TypeVar("_T")


class _CollectionQueryableContext(
    Generic[_TMasterEntity, _TKey, T], AbstractAsyncQueryable[T]
):
    """A collection queryable context. Which allows you to apply more complex
    query to the collection."""

    def __init__(
        self,
        collection: "AbstractCollection[_TMasterEntity, _TKey, T]",
        file_path: Path,
        mode: Any = "r",
    ) -> None:
        super().__init__()
        self._collection: "AbstractCollection[_TMasterEntity, _TKey, T]" = collection
        self._file_path = file_path
        self._mode = mode
        self._initialized = False
        self._closed = False
        self._file = None
        self._include_props: list[str] = []

    @property
    def closed(self):
        """Returns True if the context is closed."""
        return self._closed

    async def __aiter__(  # pylint: disable=invalid-overridden-method
        self,
    ) -> AsyncGenerator[T, None]:
        async for line in self.iter_lines():
            obj = self._collection.deserialize(line)
            if obj is not None:
                tracked = self._collection._get_as_tracked(obj)
                if self._include_props:
                    await self._collection.load_virtual_props_async(
                        obj.slave, *self._include_props
                    )
                yield cast(T, tracked)

    async def __aenter__(self):
        if not self._initialized:
            await self._collection.copy_main_file_async(self._file_path)
            self._initialized = True
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self.close()

    async def iter_lines(self) -> AsyncGenerator[str, None]:
        """Iterate over the lines of the file."""
        if not self._initialized:
            await self.__aenter__()  # pylint: disable=unnecessary-dunder-call

        async with aiofiles.open(self._file_path, self._mode) as tmp_file:
            self._file = tmp_file
            async for line in tmp_file:
                yield line

    async def close(self):
        """Close the context."""
        if self._file is not None:
            if not self.closed:
                await self._file.close()
                self._closed = True
        os.remove(self._file_path)

    def include(self, selector: Callable[[T], Optional[_T] | Optional[list[_T]]]):
        """Include a virtual property in the query result."""
        selected = selector(self._collection.entity_type)  # type: ignore
        if isinstance(selected, TProperty):
            self._include_props.append(
                selected.json_property_name or selected.actual_name
            )
        return self


class AbstractCollection(Generic[_TMasterEntity, _TKey, T], ABC):
    """A collection of an specified entity type. Acts like a table."""

    def __init__(self, engine: "Engine", /) -> None:
        """Create a new collection.

        Args:
            engine (`Engine`): The engine to use.
        """

        # if engine is None or not isinstance(engine, Engine):  # type: ignore
        #     raise ValueError("engine must be an instance of Engine")
        self._engine = engine

        self._main_file_lock = asyncio.Lock()
        self._main_iter_ctx: Optional[
            _CollectionQueryableContext[_TMasterEntity, _TKey, T]
        ] = None
        self._entity_trackers: dict[_TKey, _EntityTracker[_TKey, T]] = {}

    async def __aenter__(self):
        self._main_iter_ctx = self.get_queryable()
        return self._main_iter_ctx

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self._main_iter_ctx is not None:
            if not self._main_iter_ctx.closed:
                await self._main_iter_ctx.close()
            self._main_iter_ctx = None

    async def __aiter__(self):
        async with self.get_queryable() as tmp_file:
            async for data in tmp_file:
                yield data

    def __ilshift__(self, entity: tuple[T, ...] | T):
        if isinstance(entity, tuple):
            self.add_range(*entity)
        else:
            self.add(entity)
        return self

    def __irshift__(self, entity: tuple[T, ...] | T):
        if isinstance(entity, tuple):
            self.delete_range(*entity)
        else:
            self.delete(entity)
        return self

    def __rshift__(self, _):
        raise NotImplementedError

    def __lshift__(self, _):
        raise NotImplementedError

    @abstractmethod
    def _check_by_id(self, line_of: str, __id: _TKey) -> bool:
        ...

    @abstractmethod
    def _get_line_id(self, line_of: str) -> _TKey:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the collection."""

    @property
    @abstractmethod
    def entity_type(self) -> type[T]:
        """Get the type of the entity."""

    @property
    @abstractmethod
    def master_entity_factory(self) -> MasterEntityFactory[_TMasterEntity, _TKey, T]:
        """Get the factory for the master entity."""

    @property
    @abstractmethod
    def qa(self) -> QueryFactory[T]:
        """Get the factory for the query builder."""

    @final
    @property
    def master_entity_type(self):
        """Get the type of the master entity."""
        return self.master_entity_factory.master_entity_type

    @final
    @property
    def configuration(
        self,
    ) -> Optional[
        "CollectionConfiguration[AbstractCollection[_TMasterEntity, _TKey, T]]"
    ]:
        """Get the configuration of the collection."""
        return self._engine.get_collection_config(self.entity_type)  # type: ignore

    def _get_tracker(self, entity: T) -> _EntityTracker[_TKey, T]:
        """Get the tracker for the given entity."""
        tracking_id = getattr(entity, "__tracking_id__", None)
        if tracking_id is None:
            raise ValueError("The is not tracking.")
        return self._entity_trackers[tracking_id]

    def _tracked(self, entity: MasterEntity[_TKey, T]) -> _EntityTracker[_TKey, T]:
        """Get the tracker for the given entity."""
        tracker = _EntityTracker(entity.id, entity)
        setattr(entity.slave, "__tracking_id__", tracker.key)
        self._entity_trackers[tracker.key] = tracker
        return tracker

    def _get_as_tracked(self, entity: MasterEntity[_TKey, T]) -> T:
        """Get the tracker for the given entity."""
        return self._tracked(entity).entity

    def _create_master_entity(self, entity: T) -> MasterEntity[_TKey, T]:
        return self.master_entity_factory(entity)

    @final
    def _collection_path_builder(self):
        return self._engine.get_base_path(self) / self.name

    @final
    def _collection_tmp_path_builder(self, __id: Optional[str] = None):
        return self._engine.get_base_path(self) / f"__{self.name}_{__id}__"

    @final
    def _collection_exists(self) -> bool:
        collection_path = self._collection_path_builder()
        return collection_path.exists()

    @final
    async def _create_collection(self):
        collection_path = self._collection_path_builder()
        async with aiofiles.open(collection_path, "w") as file:
            await file.write("")

    @final
    async def _ensure_collection_exists(self) -> None:
        async with self._main_file_lock:
            if not self._collection_exists():
                await self._create_collection()

    def _get_reference_prop(self, entity: TEntity, refers_to: str):
        for virt_prop in entity.get_properties():
            if isinstance(virt_prop, ReferenceProperty):
                if virt_prop.actual_name == refers_to:
                    return virt_prop
        return None

    @final
    async def _manage_referral_properties(self, entity: MasterEntity[_TKey, T]):
        for prop in entity.slave.get_properties():  # type: ignore
            if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                values: TEntity | list[TEntity] = getattr(
                    entity.slave, prop.actual_name
                )

                col = self._engine.get_collection(prop.type_of_entity)

                if not isinstance(values, list):
                    values = [values]
                else:
                    for value in values:
                        reference = self._get_reference_prop(value, prop.refers_to)
                        if reference is not None:
                            # get if the value exists for this property
                            tracking_id = col.resolve_tracked_entity_id(value)
                            if tracking_id is None:
                                setattr(value, reference.actual_name, entity.id)
                                col.add(value)  # type: ignore
                            else:
                                saved_value = await col.get_first_async(
                                    prop.refers_to, entity.id
                                )
                                if saved_value is None:
                                    col.add(value)  # type: ignore
                                else:
                                    col.replace_entity(saved_value, value)
                        else:
                            raise TypeError(
                                f"No ReferenceProperty found for {prop.refers_to}."
                            )
                    delattr(entity.slave, prop.actual_name)
                    await col.save_changes_async()

    async def _care_about_virtual_props(self, master: MasterEntity[_TKey, T]):
        col_config = self.configuration
        if col_config is None:
            return

        for prop in master.slave.get_properties():  # type: ignore
            if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                prop_config = col_config.get_property_config(prop.actual_name)
                if prop_config is None:
                    continue

                match prop_config.delete_action.value:
                    case "delete_entity":
                        col = self._engine.get_collection(prop.type_of_entity)
                        async for item in self.iter_referenced_by_async(
                            master.slave,
                            lambda _: prop,  # pylint: disable=cell-var-from-loop
                        ):  # type: ignore
                            col.delete(item)

                        await col.save_changes_async()

                    case "delete_reference":
                        async for item in self.iter_referenced_by_async(
                            master.slave,
                            lambda _: prop,  # pylint: disable=cell-var-from-loop
                        ):  # type: ignore
                            setattr(item, prop.refers_to, None)

                        await self._engine.get_collection(
                            prop.type_of_entity
                        ).save_changes_async()

                    case "ignore":
                        continue

    async def _save_changes(self) -> int:
        updated_data: dict[str, dict[_TKey, MasterEntity[_TKey, T]]] = {
            "updated": {},
            "created": {},
            "deleted": {},
        }
        for key in tuple(self._entity_trackers.keys()):
            tracked = self._entity_trackers[key]

            match tracked.tracking_mode:
                case TrackingMode.DELETE:
                    updated_data["deleted"][tracked.key] = tracked.master_entity
                case TrackingMode.UPDATE:
                    if tracked.modified:
                        updated_data["updated"][tracked.key] = tracked.master_entity
                case TrackingMode.CREATE:
                    updated_data["created"][tracked.key] = tracked.master_entity

        changes_made_count = 0
        if any(any(mode) for mode in updated_data.values()):
            await self._ensure_collection_exists()
            async with self._main_file_lock:
                file_path = self._collection_path_builder()
                tmp_path = self._collection_tmp_path_builder()
                modified = False
                tmp_file_created = False

                # Deal with add.
                if updated_data["created"]:
                    async with aiofiles.open(file_path, "a") as file:
                        for entity in updated_data["created"].values():
                            await self._manage_referral_properties(entity)
                            data = json.dumps(serialize(entity))
                            await file.write(data + "\n")
                            changes_made_count += 1

                # Deal with update or delete.
                if updated_data["deleted"] or updated_data["updated"]:
                    async with aiofiles.open(file_path, "r") as file:
                        async with aiofiles.open(tmp_path, "w") as tmp_f:
                            tmp_file_created = True
                            async for line in file:
                                line_id = self._get_line_id(line)

                                if line_id in updated_data["deleted"]:
                                    await tmp_f.write("")
                                    modified = True
                                    changes_made_count += 1
                                elif line_id in updated_data["updated"]:
                                    entity = updated_data["updated"][line_id]
                                    await self._manage_referral_properties(entity)
                                    data = json.dumps(serialize(entity))
                                    await tmp_f.write(data + "\n")
                                    modified = True
                                    changes_made_count += 1
                                else:
                                    await tmp_f.write(line)
                if modified:
                    os.remove(file_path.absolute())
                    os.rename(tmp_path.absolute(), file_path.absolute())

                    for entity in updated_data["deleted"].values():
                        await self._care_about_virtual_props(entity)  # type: ignore
                else:
                    if tmp_file_created:
                        os.remove(tmp_path.absolute())

                # clean up trackers
                for tracking_mode in updated_data.values():
                    for tracker_key in tracking_mode:
                        tracker = self._entity_trackers.pop(tracker_key)
                        delattr(tracker.entity, "__tracking_id__")
        return changes_made_count

    def deserialize(self, data: str) -> Optional[MasterEntity[_TKey, T]]:
        """Deserialize a string into a MasterEntity of this collection."""
        return deserialize(self.master_entity_type, json.loads(data))

    async def save_changes_async(self) -> int:
        """Saves all changes you have made since last call, including add,
        update or delete entities."""
        return await self._save_changes()

    def set_tracking_mode(self, entity: T, mode: TrackingMode):
        """Manually sets tracking mode for entity. (You should not use this usually)"""
        tracker = self._get_tracker(entity)
        if tracker.tracking_mode == mode:
            return
        tracker.set_tracking_mode(mode)

    def replace_entity(self, old_entity: T, new_entity: T) -> T:
        """Replace whole entity with another of same type,
        useful for updating entity."""
        if not isinstance(old_entity, self.entity_type) or not isinstance(
            new_entity, self.entity_type
        ):
            raise TypeError(f"Both entities should an instance of {self.entity_type}")

        tracking_id = self.resolve_tracked_entity_id(old_entity)
        if tracking_id is None:
            raise ValueError("Entity is not tracked.")

        setattr(new_entity, "__tracking_id__", tracking_id)
        self._entity_trackers[tracking_id].replace_entity(new_entity)
        return new_entity

    def get_queryable(self) -> _CollectionQueryableContext[_TMasterEntity, _TKey, T]:
        """Get an queryable context for this collection."""
        __id = str(uuid4())
        return _CollectionQueryableContext(
            self, self._collection_tmp_path_builder(__id), "rb"
        )

    async def get_async(self, __id: _TKey) -> Optional[T]:
        """Get an entity by its id.

        Args:
            __id (`str`): The id of the entity.
        """

        async with self.get_queryable() as tmp_file:
            async for line in tmp_file.iter_lines():
                if self._check_by_id(line, __id):
                    data = self.deserialize(line)
                    if data is not None:
                        return self._get_as_tracked(data)
        return None

    async def copy_main_file_async(self, dest_path: Path):
        """Copy the main file to a another file."""
        await self._ensure_collection_exists()
        main_file = self._collection_path_builder()

        async with self._main_file_lock:
            shutil.copyfile(main_file.absolute(), dest_path.absolute())

    async def find_all_async(
        self, query: QueryBuilder[T, Any], /
    ) -> AsyncGenerator[T, None]:
        """Find all entities that match the query.

        Args:
            query (`QueryBuilder`): The query to match.
        """

        selector = "slave." + query.field_name

        async with self.get_queryable() as tmp_file:
            async for line in tmp_file.iter_lines():
                for item in ijson.items(line, selector):
                    if query.match(item):
                        data = self.deserialize(line)
                        if data is not None:
                            yield self._get_as_tracked(data)
                        break

    async def find_one_async(self, query: QueryBuilder[T, Any], /) -> Optional[T]:
        """Find one entity that match the query.

        Args:
            query (`QueryBuilder`): The query to match.
        """

        async for item in self.find_all_async(query):
            return item
        return None

    @overload
    def iterate_by_async(
        self, selector: str, __value: Any, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): The name of the property
            (You can use something like `item.name`,
            but The item should be an EmbedEntity).
            __value (`Any`): The value of the property.
        """

    @overload
    def iterate_by_async(
        self, selector: Callable[[T], _T], __value: _T, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): A function to select a property
            (Can't allow nested props).
            __value (`Any`): The value of the property.
        """

    async def iterate_by_async(
        self, selector: str | Callable[[T], _T], __value: _T, /
    ) -> AsyncGenerator[T, None]:
        """Iterate over all entities that have a certain property value.

        Args:
            selector (`str`): The name of the property
            (You can use something like `item.name`,
            but The item should be an EmbedEntity).
            __value (`Any`): The value of the property.
        """

        if callable(selector):
            prop = selector(self.entity_type)  # type: ignore
            if isinstance(prop, TProperty):
                selector = prop.json_property_name or prop.actual_name

        selector = "slave." + selector  # type: ignore

        async with self.get_queryable() as tmp_file:
            async for line in tmp_file.iter_lines():
                for item in ijson.items(line, selector):
                    if item == __value:
                        data = self.deserialize(line)
                        if data is not None:
                            yield self._get_as_tracked(data)

    @overload
    def get_first_async(
        self, selector: str, __value: Any
    ) -> Coroutine[Any, Any, Optional[T]]:
        """Get the first entity that has a certain property value."""

    @overload
    def get_first_async(
        self, selector: Callable[[T], _T], __value: _T
    ) -> Coroutine[Any, Any, Optional[T]]:
        """Get the first entity that has a certain property value."""

    async def get_first_async(
        self, selector: str | Callable[[T], _T], __value: _T
    ) -> Optional[T]:
        """Get the first entity that has a certain property value."""

        async for item in self.iterate_by_async(selector, __value):
            return item
        return None

    async def drop_async(self) -> None:
        """Drop the collection."""

        async with self._main_file_lock:
            if self._collection_exists():
                os.remove(self._collection_path_builder().absolute())

    def delete(self, entity: T) -> _EntityTracker[_TKey, T]:
        """Delete an entity.

        Args:
            entity (`T`): The entity to delete.

        Returns:
            `EntityTracker[TKey, T]`: The tracker for the deleted entity.
        """

        tracked = self._get_tracker(entity)
        tracked.set_tracking_mode_delete()
        return tracked

    def delete_range(self, *entities: T) -> list[_EntityTracker[_TKey, T]]:
        """Delete many entities.

        Args:
            entities (`Iterable[T]`): The entities to delete.

        Returns:
            `List[EntityTracker[TKey, T]]`: The trackers for the deleted entities.
        """
        return [self.delete(x) for x in entities]

    def add(self, entity: T) -> _EntityTracker[_TKey, T]:
        """Add an entity to the collection.

        Args:
            entity (`T`): The entity to add to the collection.

        Returns:
            `EntityTracker[TKey, T]`: The tracker for the added entity.
        """

        mastered = self._create_master_entity(entity)
        tracking = self._tracked(mastered)
        tracking.set_tracking_mode_create()
        return tracking

    def add_range(self, *entities: T) -> list[_EntityTracker[_TKey, T]]:
        """Add multiple entities to the collection."""

        return [self.add(entity) for entity in entities]

    async def load_virtual_props_async(self, entity: T, *props: str):
        """Load all virtual properties based on references."""

        if isinstance(entity, TEntity):
            for prop in entity.get_properties():

                if props and prop.actual_name not in props:
                    continue

                except_one = False
                if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                    except_one = isinstance(prop, VirtualComplexProperty)
                    # get a collection for reference type
                    col = self._engine.get_collection(prop.type_of_entity)

                    # TODO: Is this performance wise ?
                    results: list[Any] = []
                    tracker = self._get_tracker(entity)
                    async for item in col.iterate_by_async(prop.refers_to, tracker.key):
                        if except_one:
                            setattr(entity, prop.actual_name, item)
                            return
                        else:
                            results.append(item)
                    setattr(entity, prop.actual_name, results)
        else:
            raise TypeError("Entity should be an instance of TEntity.")

    async def iter_referenced_by_async(
        self,
        entity: T,
        selector: Callable[[type[T]], Optional[_T] | Optional[list[_T]]],
    ) -> AsyncIterable[_T]:
        """Iterate over all virtual objects of an property.

        Args:
            entity (`T`): The reference entity.
            selector (`Callable[[type[T]], _T | list[_T]]`):
            The property selector should select a virtual prop.
        """

        if isinstance(entity, TEntity):
            prop = selector(self.entity_type)
            if isinstance(prop, (VirtualComplexProperty, VirtualListProperty)):
                # get a collection for reference type
                col = self._engine.get_collection(prop.type_of_entity)

                tracker = self._get_tracker(entity)
                async for item in col.iterate_by_async(prop.refers_to, tracker.key):
                    yield item  # type: ignore
        else:
            raise TypeError("Entity should be an instance of TEntity.")

    async def purge_async(self):
        """Purge the collection."""
        async with self._main_file_lock:
            os.remove(self._collection_path_builder().absolute())

    async def count_async(self) -> int:
        """Count the number of entities in the collection."""

        await self._ensure_collection_exists()
        async with self as iter_ctx:
            count = 0
            async for _ in iter_ctx.iter_lines():
                count += 1
            return count

    def resolve_tracked_entity_id(self, entity: T) -> Optional[_TKey]:
        """Resolve an entity's id if it's tracked."""
        return getattr(entity, "__tracking_id__", None)


class Collection(Generic[T], AbstractCollection[UuidMasterEntity, str, T]):
    """A collection of an specified entity type. Acts like a table."""

    def __init__(
        self, engine: "Engine", entity_type: type[T], name: Optional[str] = None, /
    ) -> None:
        """Create a new collection.

        Args:
            engine (`Engine`): The engine to use.
            entity_type (`type`): The type of the entity.
            name (`str`, optional): The name of the collection.
            Defaults to name of entity_type.
        """

        if entity_type is None or not isinstance(entity_type, type):  # type: ignore
            raise ValueError("entity_type must be a type")

        self._name = name or entity_type.__name__

        if not issubclass(entity_type, TEntity):  # type: ignore
            raise TypeError(
                f"The entity_type must be a subclass of {TEntity.__name__}."
            )

        self._entity_type: type[T] = entity_type  # type: ignore
        self._master_entity_factory = UuidMasterEntityFactory(self._entity_type)
        self._query_factory = QueryFactory(self._entity_type)
        super().__init__(engine)

    def _check_by_id(self, line_of: str | bytes, __id: str) -> bool:
        __found = self._get_line_id(line_of)
        return __found == __id

    def _get_line_id(self, line_of: str | bytes) -> str:
        if isinstance(line_of, str):
            return line_of[10:46]
        return line_of[10:46].decode()

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
    def master_entity_factory(self) -> MasterEntityFactory[UuidMasterEntity, str, T]:
        return self._master_entity_factory

    @final
    @property
    def qa(self) -> QueryFactory[T]:
        return self._query_factory
