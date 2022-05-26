from abc import ABC
import inspect

from pathlib import Path
from typing import Any, Generic, Optional, final, overload

from ..serialization._shared import T
from ._collection import Collection


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
    def __get__(self, obj: object, objtype: type[object]) -> Collection[T]:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "__Collection__[T]" | Collection[T]:
        if obj is None:
            return self
        return obj.get_collection(self._entity_type)  # type: ignore

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


class Engine(ABC):
    """Initializes the engine.

    Base of everything that you gonna use, Should be used as base class of your engine"""

    @overload
    def __init__(self, base_path: Path):
        """Initializes the engine.

        Base of everything that you gonna use, Should be used as base class of your engine

        Args:
            base_path (`Path`): The base path of the engine.
        """
        ...

    @overload
    def __init__(self, base_path: str):
        """Initializes the engine.

        Base of everything that you gonna use, Should be used as base class of your engine

        Args:
            base_path (`str`): The base path of the engine.
        """
        ...

    def __init__(self, base_path: Path | str):
        if isinstance(base_path, str):
            self._base_path = Path(base_path)
        else:
            self._base_path = base_path

        self.__initialize_path(self._base_path)
        self.__collections: dict[type[Any], Collection[Any]] = {}
        self.__set_collections()
        self.__initialized = True

    def __set_collections(self):
        for _, col in inspect.getmembers(type(self)):
            if isinstance(col, __Collection__):
                if col.entity_type in self.__collections:  # type: ignore
                    raise CollectionEntityTypeDuplicated(
                        col.collection_name, col.entity_type  # type: ignore
                    )
                collection = Collection(self, col.entity_type, col.collection_name)  # type: ignore
                self.__collections[col.entity_type] = collection  #  type: ignore

    def __initialize_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    @final
    def get_base_path(self, collection: Collection[Any]) -> Path:
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
    def get_collection(self, entity_type: type[T]) -> Optional[Collection[T]]:
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
    ) -> Collection[T]:
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

    @final
    @staticmethod
    def set(entity_type: type[T]) -> __Collection__[T]:
        """Sets a collection (staticmethod).

        Args:
            entity_type (`type[T]`): The entity type of the collection.

        Returns:
            `__Collection__[T]`: The descriptor of the collection. can only be used as an engine's `ClassVar`.
        """
        return __Collection__(entity_type)
