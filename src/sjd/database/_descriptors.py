from typing import Any, Generic, TypeVar, cast, final, overload, TYPE_CHECKING

from ..serialization._shared import T
from ._collection import AbstractCollection, _TMasterEntity, _TKey

if TYPE_CHECKING:
    from ._engine import Engine


class _Collection(Generic[_TMasterEntity, _TKey, T]):
    """This is a descriptor of Collection. Can only be used in an engine class as
    `ClassVar`."""

    def __init__(self, entity_type: type[T]) -> None:
        """This is a descriptor of Collection."""
        super().__init__()
        self._entity_type = entity_type

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._collection_name = name  # pylint: disable=attribute-defined-outside-init

    @final
    @property
    def collection_name(self) -> str:
        """The name of the collection."""
        return self._collection_name

    @final
    @property
    def entity_type(self) -> type[T]:
        """The type of the entity."""
        return self._entity_type

    @overload
    def __get__(
        self, obj: None, objtype: None
    ) -> "_Collection[_TMasterEntity, _TKey, T]":
        ...

    @overload
    def __get__(
        self, obj: object, objtype: type[object]
    ) -> AbstractCollection[Any, Any, T]:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "_Collection[_TMasterEntity, _TKey, T]" | AbstractCollection[Any, Any, T]:
        if obj is None:
            return self
        return cast("Engine", obj).get_collection(self._entity_type)

    def __set__(self, obj: object, value: T) -> None:
        raise AttributeError("Engine collections are read-only.")


_TCol = TypeVar("_TCol", bound=AbstractCollection[Any, Any, Any])


class _TypedCollection(
    Generic[_TMasterEntity, _TKey, T, _TCol], _Collection[_TMasterEntity, _TKey, T]
):
    """This is a descriptor of Typed Collection. Can only be used in an engine
    class as `ClassVar`."""

    def __init__(
        self,
        entity_type: type[T],
        collection_type: type[AbstractCollection[Any, Any, T]],
    ) -> None:
        """This is a descriptor of Collection."""
        super().__init__(entity_type)
        self._collection_type = collection_type

    @final
    @property
    def collection_type(self):
        """The type of the collection."""
        return self._collection_type

    @overload
    def __get__(
        self, obj: None, objtype: None
    ) -> "_TypedCollection[_TMasterEntity, _TKey, T, _TCol]":
        ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> _TCol:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "_TypedCollection[_TMasterEntity, _TKey, T, _TCol]" | _TCol:
        if obj is None:
            return self
        t_col = cast("Engine", obj).get_collection(self._entity_type)
        return cast(_TCol, t_col)

    def __set__(self, obj: object, value: T) -> None:
        raise AttributeError("can't set attribute")
