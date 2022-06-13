# pylint: disable=invalid-name

from abc import ABC
import re
from typing import Callable, Generic, TypeVar

from ._query_builder import QueryBuilder, _TModel, _TValue


class _SupportsGreaterThan(Generic[_TValue], ABC):
    def __gt__(self, other: _TValue) -> bool:
        ...


_TSupportsGreaterThan = TypeVar("_TSupportsGreaterThan", bound=_SupportsGreaterThan)


class _SupportsLessThan(Generic[_TValue], ABC):
    def __lt__(self, other: _TValue) -> bool:
        ...


_TSupportsLessThan = TypeVar("_TSupportsLessThan", bound=_SupportsLessThan)


class _SupportsMemberOf(Generic[_TValue], ABC):
    def __contains__(self, other: _TValue) -> bool:
        ...


_TSupportsMemberOf = TypeVar("_TSupportsMemberOf", bound=_SupportsMemberOf)


_TInput = TypeVar("_TInput")


class _ValuedQueryBuilder(
    Generic[_TModel, _TValue, _TInput], QueryBuilder[_TModel, _TValue]
):
    def __init__(
        self,
        entity_type: type[_TModel],
        selector: Callable[[_TModel], _TValue],
        value: _TInput,
        /,
    ) -> None:
        super().__init__(selector)
        self._entity_type = entity_type
        self._value = value


class _EqualityQueryBuilder(
    Generic[_TModel, _TValue], _ValuedQueryBuilder[_TModel, _TValue, _TValue]
):
    """An equality query builder."""

    def __check__(self, value_to_check: _TValue, /) -> bool:
        return value_to_check == self._value


class _InequalityQueryBuilder(
    Generic[_TModel, _TValue], _ValuedQueryBuilder[_TModel, _TValue, _TValue]
):
    """An inequality query builder."""

    def __check__(self, value_to_check: _TValue, /) -> bool:
        return value_to_check != self._value


class _GreaterThanQueryBuilder(
    Generic[_TModel, _TSupportsGreaterThan],
    _ValuedQueryBuilder[_TModel, _TSupportsGreaterThan, _TSupportsGreaterThan],
):
    """A greater than query builder."""

    def __check__(self, value_to_check: _TSupportsGreaterThan, /) -> bool:
        return value_to_check > self._value


class _LessThanQueryBuilder(
    Generic[_TModel, _TSupportsLessThan],
    _ValuedQueryBuilder[_TModel, _TSupportsLessThan, _TSupportsLessThan],
):
    """A less than query builder."""

    def __check__(self, value_to_check: _TSupportsLessThan, /) -> bool:
        return value_to_check < self._value


class _MemberOfQueryBuilder(
    Generic[_TModel, _TSupportsMemberOf],
    _ValuedQueryBuilder[_TModel, _TSupportsMemberOf, _TSupportsMemberOf],
):
    """A member of query builder."""

    def __check__(self, value_to_check: _TSupportsMemberOf, /) -> bool:
        return value_to_check in self._value


class _NotMemberOfQueryBuilder(
    Generic[_TModel, _TSupportsMemberOf],
    _ValuedQueryBuilder[_TModel, _TSupportsMemberOf, _TSupportsMemberOf],
):
    """A not member of query builder."""

    def __check__(self, value_to_check: _TSupportsMemberOf, /) -> bool:
        return value_to_check not in self._value


class _RegexQueryBuilder(
    Generic[_TModel], _ValuedQueryBuilder[_TModel, str, re.Pattern]
):
    """A regex query builder."""

    def __check__(self, value_to_check: str, /) -> bool:
        return self._value.search(value_to_check) is not None


class QueryFactory(Generic[_TModel]):
    """A factory for creating queries."""

    def __init__(self, entity_type: type[_TModel]) -> None:
        self._entity_type = entity_type

    def eq(
        self, selector: Callable[[_TModel], _TValue], value: _TValue
    ) -> QueryBuilder[_TModel, _TValue]:
        """Creates an equality query builder."""
        return _EqualityQueryBuilder(self._entity_type, selector, value)

    def ne(
        self, selector: Callable[[_TModel], _TValue], value: _TValue
    ) -> QueryBuilder[_TModel, _TValue]:
        """Creates an inequality query builder."""
        return _InequalityQueryBuilder(self._entity_type, selector, value)

    def gt(
        self,
        selector: Callable[[_TModel], _TSupportsGreaterThan],
        value: _TSupportsGreaterThan,
    ) -> QueryBuilder[_TModel, _TSupportsGreaterThan]:
        """Creates a greater than query builder."""
        return _GreaterThanQueryBuilder(self._entity_type, selector, value)

    def lt(
        self,
        selector: Callable[[_TModel], _TSupportsLessThan],
        value: _TSupportsLessThan,
    ) -> QueryBuilder[_TModel, _TSupportsLessThan]:
        """Creates a less than query builder."""
        return _LessThanQueryBuilder(self._entity_type, selector, value)

    def in_(
        self,
        selector: Callable[[_TModel], _TSupportsMemberOf],
        value: _TSupportsMemberOf,
    ) -> QueryBuilder[_TModel, _TSupportsMemberOf]:
        """Creates a member of query builder."""
        return _MemberOfQueryBuilder(self._entity_type, selector, value)

    def not_in(
        self,
        selector: Callable[[_TModel], _TSupportsMemberOf],
        value: _TSupportsMemberOf,
    ) -> QueryBuilder[_TModel, _TSupportsMemberOf]:
        """Creates a not member of query builder."""
        return _NotMemberOfQueryBuilder(self._entity_type, selector, value)

    def regex(
        self, selector: Callable[[_TModel], str], value: re.Pattern
    ) -> QueryBuilder[_TModel, str]:
        """Creates a regex query builder."""
        return _RegexQueryBuilder(self._entity_type, selector, value)
