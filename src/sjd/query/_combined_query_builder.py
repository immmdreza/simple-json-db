from typing import Generic

from ._abstract_builders import _AbstractCombinedQueryBuilder, _TValue


class AndQueryBuilder(Generic[_TValue], _AbstractCombinedQueryBuilder[_TValue]):
    """Combine query builders with and operator."""

    def __combinator__(self, value_to_check: _TValue, /) -> bool:
        return all(query.match(value_to_check) for query in self._builders)


class OrQueryBuilder(Generic[_TValue], _AbstractCombinedQueryBuilder[_TValue]):
    """Combine query builders with or operator."""

    def __combinator__(self, value_to_check: _TValue, /) -> bool:
        return any(query.match(value_to_check) for query in self._builders)
