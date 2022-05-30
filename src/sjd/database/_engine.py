import inspect

from pathlib import Path
from typing import Any, Optional, TypeVar, final

from ..entity import TEntity
from ..serialization._shared import T
from ._collection import AbstractCollection, Collection
from ._descriptors import __Collection__, __Typed_Collection__, _TCol  # type: ignore
from ._configuration import EngineConfiguration, CollectionConfiguration


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


_TEngine = TypeVar("_TEngine", bound="Engine")


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

        self.__configs = EngineConfiguration(type(self))

    def __setitem__(self, name: str, entity_type: type[Any]) -> None:
        """Manually registers a collection."""
        self.register_collection(entity_type, name)

    def __getitem__(self, entity_type: type[T]) -> AbstractCollection[T]:
        """Gets a collection by entity type.

        Args:
            entity_type (`type[T]`): The entity type of the collection.
        """
        return self.get_collection(entity_type)

    def __set_collections(self):
        for _, col in inspect.getmembers(type(self)):
            if isinstance(col, __Collection__):
                self.register_collection(col.entity_type, col.collection_name)  # type: ignore
            elif isinstance(col, __Typed_Collection__):
                self.register_typed_collection(col.collection_type)

    def __initialize_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    @property
    def _configs(self: _TEngine) -> EngineConfiguration[_TEngine]:
        """Gets the engine configuration."""
        return self.__configs  # type: ignore

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
    def get_collection(self, entity_type: type[T]) -> AbstractCollection[T]:
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
            self.register_collection(entity_type)
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

        if entity_type is None or not issubclass(entity_type, TEntity):
            raise ValueError("entity_type must be a TEntity.")

        col = Collection(self, entity_type, name)
        self.__collections[entity_type] = col
        return col  # type: ignore

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

    def get_collection_config(
        self, _entity_type: type[_TCol]
    ) -> Optional[CollectionConfiguration[AbstractCollection[_TCol]]]:
        """Gets the collection configuration.

        Args:
            _entity_type (`type[_TCol]`): The entity type of the collection.
        """
        return self.__configs.get_collection_config(_entity_type)
