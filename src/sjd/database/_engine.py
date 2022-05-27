import inspect

from pathlib import Path
from typing import Any, Generic, Optional, TypeVar, cast, final, overload

from ..entity import TEntity
from ..serialization._shared import T
from ._collection import AbstractCollection, Collection


class __Collection__(Generic[T]):
    """This is a descriptor of Collection. Can only be used in an engine class as `ClassVar`."""

    def __init__(self, entity_type: type[T]) -> None:
        """This is a descriptor of Collection."""
        super().__init__()
        self._entity_type = entity_type

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._collection_name = name

    @final
    @property
    def collection_name(self) -> str:
        return self._collection_name

    @final
    @property
    def entity_type(self) -> type[T]:
        return self._entity_type

    @overload
    def __get__(self, obj: None, objtype: None) -> "__Collection__[T]":
        ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> AbstractCollection[T]:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "__Collection__[T]" | AbstractCollection[T]:
        if obj is None:
            return self
        col = cast("Engine", obj).get_collection(self._entity_type)
        if col is None:
            raise AttributeError(f"Can't get such collection {self._entity_type}")
        return col

    def __set__(self, obj: object, value: T) -> None:
        raise AttributeError("Engine collections are read-only.")


_TCol = TypeVar("_TCol", bound=AbstractCollection[Any])


class __Typed_Collection__(Generic[T, _TCol]):
    """This is a descriptor of Typed Collection. Can only be used in an engine class as `ClassVar`."""

    def __init__(
        self, entity_type: type[T], collection_type: type[AbstractCollection[T]]
    ) -> None:
        """This is a descriptor of Collection."""
        super().__init__()
        self._collection_type = collection_type
        self._entity_type = entity_type

    @final
    @property
    def collection_type(self):
        return self._collection_type

    @final
    @property
    def entity_type(self) -> type[T]:
        return self._entity_type

    @overload
    def __get__(self, obj: None, objtype: None) -> "__Typed_Collection__[T, _TCol]":
        ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> _TCol:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "__Typed_Collection__[T, _TCol]" | _TCol:
        if obj is None:
            return self
        t_col = cast("Engine", obj).get_collection(self._entity_type)
        if t_col is None:
            raise AttributeError(
                f"Can't get such typed collection {self._entity_type}, {self._collection_type}"
            )
        return cast(_TCol, t_col)

    def __set__(self, obj: object, value: T) -> None:
        raise AttributeError("can't set attribute")


class EngineNotInitialized(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Engine is not initialized! Did you missed __init__ or super().__init__ inside it?"
        )


class CollectionEntityTypeDuplicated(Exception):
    def __init__(self, collection_name: str, entity_type: type[Any]) -> None:
        super().__init__(
            f"Collection {collection_name} already has entity type {entity_type}"
        )


class CollectionNotRegistered(Exception):
    def __init__(self, collection_name: str) -> None:
        super().__init__(
            f"Collection {collection_name} is not registered. Did you done something wired?"
        )


class Engine:
    """Initializes the engine.

    Base of everything that you gonna use, Should be used as base class of your engine"""

    def __init__(self, base_path: Path | str):
        """Initializes the engine.

        Base of everything that you gonna use, Should be used as base class of your engine

        Args:
            base_path (`Path` | `str`): The base path of the engine.
        """

        if isinstance(base_path, str):
            self._base_path = Path(base_path)
        else:
            self._base_path = base_path

        self.__initialized = True
        self.__initialize_path(self._base_path)
        self.__collections: dict[type[Any], AbstractCollection[Any]] = {}
        self.__set_collections()

    def __setitem__(self, name: str, entity_type: type[Any]) -> None:
        """Manually registers a collection."""
        self.register_collection(entity_type, name)

    def __getitem__(self, entity_type: type[T]) -> AbstractCollection[T]:
        """Gets a collection by entity type.

        Args:
            entity_type (`type[T]`): The entity type of the collection.
        """
        if (col := self.get_collection(entity_type)) is not None:
            return col
        raise KeyError(f"Collection of type {entity_type} is not registered")

    def __set_collections(self):
        for _, col in inspect.getmembers(type(self)):
            if isinstance(col, __Collection__):
                self.register_collection(col.entity_type, col.collection_name)  # type: ignore
            elif isinstance(col, __Typed_Collection__):
                self.register_typed_collection(col.collection_type)

    def __initialize_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    @final
    def get_base_path(self, collection: AbstractCollection[Any]) -> Path:
        """Returns the base path of the engine.

        Args:
            collection (`Collection[Any]`): The collection that requested the path.

        Returns:
            `Path`: The base path of the engine.
        """

        if not self.__initialized:
            raise EngineNotInitialized()

        if collection.entity_type not in self.__collections:
            raise CollectionNotRegistered(collection.name)

        """Returns the base path of the engine."""
        return self._base_path

    @final
    def get_collection(self, entity_type: type[T]) -> Optional[AbstractCollection[T]]:
        """Returns the collection of the entity type.

        Args:
            entity_type (`type[T]`): The entity type of the collection.

        Raises:
            `EngineNotInitialized`: If the engine is not initialized.

        Returns:
            `Optional[Collection[T]]`: The collection of the entity type. `None` if not found.
        """
        if not self.__initialized:
            raise EngineNotInitialized()
        if entity_type not in self.__collections:
            return None
        return self.__collections[entity_type]

    @final
    def purge(self) -> None:
        """Purges the engine."""
        for collection in self.__collections.values():
            collection.purge()
        self._base_path.rmdir()

    def register_collection(
        self, entity_type: type[T], name: Optional[str] = None, /
    ) -> AbstractCollection[T]:
        """Manually registers a collection.

        Args:
            entity_type (`type[T]`): The entity type of the collection.
            name (`Optional[str]`, optional): The name of the collection. Defaults to `Type.__name__`.

        Raises:
            `EngineNotInitialized`: If the engine is not initialized.
            `CollectionEntityTypeDuplicated`: If the entity type is already registered.

        Returns:
            `Collection[T]`: The registered collection.
        """
        if not self.__initialized:
            raise EngineNotInitialized()
        if entity_type in self.__collections:
            raise CollectionEntityTypeDuplicated(
                name or entity_type.__name__, entity_type
            )
        col = Collection(self, entity_type, name)
        self.__collections[entity_type] = col
        return col

    def register_typed_collection(
        self, collection: type[AbstractCollection[T]]
    ) -> AbstractCollection[T]:
        if not self.__initialized:
            raise EngineNotInitialized()

        col = collection(self)

        if col.entity_type is None or not issubclass(col.entity_type, TEntity):  # type: ignore
            raise ValueError("entity_type must be a TEntity.")

        if col.entity_type in self.__collections:
            raise CollectionEntityTypeDuplicated(col.name, col.entity_type)
        self.__collections[col.entity_type] = col
        return col

    @final
    @staticmethod
    def set(entity_type: type[T]) -> __Collection__[T]:
        """Sets a collection (staticmethod).

        Args:
            entity_type (`type[T]`): The entity type of the collection.

        Returns:
            `__Collection__[T]`: The descriptor of the collection. can only be used as an engine's `ClassVar`.
        """
        return __Collection__[T](entity_type)

    @final
    @staticmethod
    def typed_set(
        entity_type: type[T], collection_type: type[_TCol]
    ) -> __Typed_Collection__[T, _TCol]:
        """Sets a typed collection (staticmethod).

        Args:
            entity_type (`type[T]`): The entity type of the collection.
            collection_type (`type[_TCol]`): The type of your collection.

        Returns:
            `__Typed_Collection__[T, _TCol]`: The descriptor of the collection. can only be used as an engine's `ClassVar`.
        """
        return __Typed_Collection__[T, _TCol](entity_type, collection_type)
