from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


_TValue = TypeVar("_TValue")


class _AbstractQueryBuilder(Generic[_TValue], ABC):
    @abstractmethod
    def __check__(self, value_to_check: _TValue, /) -> bool:
        raise NotImplementedError()

    def __value_makeup__(self, value_to_check: _TValue, /) -> Any:
        return value_to_check

    def match(self, value_to_check: _TValue, /) -> bool:
        """Checks if the value is valid."""
        return self.__check__(self.__value_makeup__(value_to_check))


class _AbstractCombinedQueryBuilder(Generic[_TValue], _AbstractQueryBuilder[_TValue]):
    def __init__(self, *builders: _AbstractQueryBuilder[_TValue]) -> None:
        super().__init__()
        self._builders = builders

    @abstractmethod
    def __combinator__(self, value_to_check: _TValue, /) -> bool:
        ...

    def __check__(self, value_to_check: _TValue, /) -> bool:
        return self.__combinator__(value_to_check)
