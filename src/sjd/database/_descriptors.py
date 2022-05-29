from typing import Any, Generic, TypeVar, cast, final, overload, TYPE_CHECKING

from ..serialization._shared import T
from ._collection import AbstractCollection

if TYPE_CHECKING:
    from ._engine import Engine


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


class __Typed_Collection__(Generic[T, _TCol], __Collection__[T]):
    """This is a descriptor of Typed Collection. Can only be used in an engine class as `ClassVar`."""

    def __init__(
        self, entity_type: type[T], collection_type: type[AbstractCollection[T]]
    ) -> None:
        """This is a descriptor of Collection."""
        super().__init__(entity_type)
        self._collection_type = collection_type

    @final
    @property
    def collection_type(self):
        return self._collection_type

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
