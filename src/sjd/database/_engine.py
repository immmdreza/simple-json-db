from abc import ABC
import inspect

from pathlib import Path
from typing import Any, Generic, Optional, final, overload

from ..serialization._shared import T
from ._collection import Collection


class __Collection__(Generic[T]):
    """This is a descriptor of Collection."""

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


class Engine(ABC):
    def __init__(self, base_path: Path):
        self._base_path = base_path
        self._initialize_path(base_path)
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

    def _initialize_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    @final
    @property
    def base_path(self) -> Path:
        if not self.__initialized:
            raise EngineNotInitialized()
        """Returns the base path of the engine."""
        return self._base_path

    @final
    def get_collection(self, entity_type: type[T]) -> Optional[Collection[T]]:
        if not self.__initialized:
            raise EngineNotInitialized()
        if entity_type not in self.__collections:
            return None
        return self.__collections[entity_type]
