from datetime import datetime
from typing import Any, Callable, Generic, Optional, TypeVar

from ._abstract_builders import _AbstractQueryBuilder, _TValue
from ._combined_query_builder import AndQueryBuilder, OrQueryBuilder
from ..entity._property import TProperty


_TModel = TypeVar("_TModel")


class QueryBuilder(Generic[_TModel, _TValue], _AbstractQueryBuilder[_TValue]):
    """Builds the query."""

    def __init__(self, selector: Callable[[_TModel], _TValue], /) -> None:
        self._selector = selector
        if not callable(selector):
            raise TypeError(f"{selector} is not a callable")
        self._field_name: Optional[str] = None
        self._entity_type: Optional[type[_TModel]] = None
        self._prop: Optional[TProperty] = None

    def __value_makeup__(self, value_to_check: _TValue, /) -> Any:
        if self.prop.type_of_entity == datetime:
            if isinstance(value_to_check, str):
                return datetime.fromisoformat(value_to_check)
            raise ValueError("Excepted an string to convert to datetime.")
        return value_to_check

    @property
    def entity_type(self):
        """Type of entity."""

        if self._entity_type is None:
            raise ValueError("Entity type is not set")
        return self._entity_type

    @property
    def prop(self) -> TProperty[Any]:
        """Property type."""
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
        """Name of field."""
        if self._field_name is None:
            prop = self.prop
            self._field_name = prop.json_property_name or prop.actual_name
        return self._field_name

    def set_entity_type(self, entity_type: type[_TModel]) -> None:
        """Sets the entity type."""
        self._entity_type = entity_type

    def __and__(self, other: "QueryBuilder"):
        if isinstance(other, QueryBuilder):
            if other.entity_type == self.entity_type:
                return AndQueryBuilder(self, other)
        raise TypeError("Only queries and with same entity type can be combined.")

    def __or__(self, other: "QueryBuilder"):
        if isinstance(other, QueryBuilder):
            if other.entity_type == self.entity_type:
                return OrQueryBuilder(self, other)
        raise TypeError("Only queries and with same entity type can be combined.")
