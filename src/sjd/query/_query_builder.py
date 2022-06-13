from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, TypeVar

from ..entity._property import TProperty


_TValue = TypeVar("_TValue")
_TModel = TypeVar("_TModel")


class _AbstractQueryBuilder(Generic[_TValue], ABC):
    @property
    @abstractmethod
    def field_name(self) -> str:
        """Returns the field name."""

        raise NotImplementedError()

    @abstractmethod
    def __check__(self, value_to_check: _TValue, /) -> bool:
        raise NotImplementedError()

    def match(self, value_to_check: _TValue, /) -> bool:
        """Checks if the value is valid."""
        return self.__check__(value_to_check)


class QueryBuilder(Generic[_TModel, _TValue], _AbstractQueryBuilder[_TValue]):
    """Builds the query."""

    def __init__(self, selector: Callable[[_TModel], _TValue], /) -> None:
        self._selector = selector
        if not callable(selector):
            raise TypeError(f"{selector} is not a callable")
        self._field_name: Optional[str] = None
        self._entity_type: Optional[type[_TModel]] = None

    @property
    def field_name(self) -> str:
        if self._field_name is None:
            if self._entity_type is None:
                raise ValueError("Entity type is not set")

            prop = self._selector(self._entity_type)  # type: ignore
            if isinstance(prop, TProperty):
                self._field_name = prop.json_property_name or prop.actual_name
                return self._field_name
            raise TypeError(f"{self._selector} is not a property")
        return self._field_name

    def set_entity_type(self, entity_type: type[_TModel]) -> None:
        """Sets the entity type."""
        self._entity_type = entity_type
