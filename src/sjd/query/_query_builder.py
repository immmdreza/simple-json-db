from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Generic, Optional, TypeVar

from ..entity._property import TProperty


_TValue = TypeVar("_TValue")
_TModel = TypeVar("_TModel")


class _AbstractQueryBuilder(Generic[_TValue], ABC):
    @property
    @abstractmethod
    def prop(self) -> TProperty[Any]:
        """Property object resolved from selector"""

    @property
    @abstractmethod
    def field_name(self) -> str:
        """Returns the field name."""

        raise NotImplementedError()

    @abstractmethod
    def __check__(self, value_to_check: _TValue, /) -> bool:
        raise NotImplementedError()

    def __value_makeup__(self, value_to_check: _TValue, /) -> Any:
        if self.prop.type_of_entity == datetime:
            if isinstance(value_to_check, str):
                return datetime.fromisoformat(value_to_check)
            else:
                raise ValueError("Excepted an string to convert to datetime.")
        return value_to_check

    def match(self, value_to_check: _TValue, /) -> bool:
        """Checks if the value is valid."""
        return self.__check__(self.__value_makeup__(value_to_check))


class QueryBuilder(Generic[_TModel, _TValue], _AbstractQueryBuilder[_TValue]):
    """Builds the query."""

    def __init__(self, selector: Callable[[_TModel], _TValue], /) -> None:
        self._selector = selector
        if not callable(selector):
            raise TypeError(f"{selector} is not a callable")
        self._field_name: Optional[str] = None
        self._entity_type: Optional[type[_TModel]] = None
        self._prop: Optional[TProperty] = None

    @property
    def prop(self) -> TProperty[Any]:
        if self._prop is None:
            if self._entity_type is None:
                raise ValueError("Entity type is not set")

            prop = self._selector(self._entity_type)  # type: ignore
            if isinstance(prop, TProperty):
                self._prop = prop
            else:
                raise TypeError(f"{self._selector} is not a property")
        return self._prop

    @property
    def field_name(self) -> str:
        if self._field_name is None:
            prop = self.prop
            self._field_name = prop.json_property_name or prop.actual_name
        return self._field_name

    def set_entity_type(self, entity_type: type[_TModel]) -> None:
        """Sets the entity type."""
        self._entity_type = entity_type
