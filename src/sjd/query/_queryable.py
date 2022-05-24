from typing import Any, Callable, Generic, Optional, Iterator
from collections.abc import Iterable, AsyncIterable

from ..serialization._shared import T
from ._query import Query


class _Queryable(Generic[T]):
    def __init__(self) -> None:
        self._queries: list[Query[T]] = []

    def _new_query(self, query: Callable[[type[T]], bool]):
        self._queries.append(Query(query))
        return self

    def _check(self, against: T) -> bool:
        return all(q.check(against) for q in self._queries)

    def where(self, query: Callable[[type[T]], bool]):
        return self._new_query(query)


class Queryable(Generic[T], Iterable[T], _Queryable[T]):
    def __init__(self, _iterator: Iterable[T], /) -> None:
        super().__init__()
        self._iterator = _iterator

    def __iter__(self) -> Iterator[T]:
        for x in self._iterator:
            if self._check(x):
                yield x

    def any(self, query: Optional[Callable[[type[T]], bool]] = None) -> bool:
        if query is not None:
            self._new_query(query)

        return any(self._check(x) for x in self)

    def all(self, query: Optional[Callable[[type[T]], bool]] = None) -> bool:
        if query is not None:
            self._new_query(query)

        return all(self._check(x) for x in self)

    def first(self, query: Optional[Callable[[type[T]], bool]] = None) -> T:
        if query is not None:
            self._new_query(query)

        for x in self:
            if self._check(x):
                return x

        raise StopIteration()

    def first_or_default(
        self, query: Optional[Callable[[type[T]], bool]] = None, default: Any = None
    ) -> Optional[T]:
        if query is not None:
            self._new_query(query)

        for x in self:
            if self._check(x):
                return x
        return default

    def single(self, query: Optional[Callable[[type[T]], bool]] = None) -> T:
        if query is not None:
            self._new_query(query)
        r = None
        found = False
        for x in self:
            if self._check(x):
                if found:
                    raise ValueError("More than one element found.")
                r = x
                found = True
        if r is not None:
            return r
        raise ValueError("No element were found.")

    def single_or_default(
        self, query: Optional[Callable[[type[T]], bool]] = None, default: Any = None
    ) -> Optional[T]:
        if query is not None:
            self._new_query(query)
        r = None
        found = False
        for x in self:
            if self._check(x):
                if found:
                    raise ValueError("More than one element found.")
                r = x
                found = True
        if r is not None:
            return r
        return default

    def to_list(self) -> list[T]:
        return list(self)

    def to_tuple(self) -> tuple[T, ...]:
        return tuple(self)


class AsyncQueryable(Generic[T], AsyncIterable[T], _Queryable[T]):
    def __init__(self, _iterator: AsyncIterable[T], /) -> None:
        super().__init__()
        self._iterator = _iterator

    async def __aiter__(self):
        async for x in self._iterator:
            if self._check(x):
                yield x

    async def any(self, query: Optional[Callable[[type[T]], bool]] = None) -> bool:
        if query is not None:
            self._new_query(query)

        async for x in self:
            if self._check(x):
                return True
        return False

    async def all(self, query: Optional[Callable[[type[T]], bool]] = None) -> bool:
        if query is not None:
            self._new_query(query)

        async for x in self:
            if not self._check(x):
                return False
        return True

    async def first(self, query: Optional[Callable[[type[T]], bool]] = None) -> T:
        if query is not None:
            self._new_query(query)

        async for x in self:
            if self._check(x):
                return x

        raise StopIteration()

    async def first_or_default(
        self, query: Optional[Callable[[type[T]], bool]] = None, default: Any = None
    ) -> Optional[T]:
        if query is not None:
            self._new_query(query)

        async for x in self:
            if self._check(x):
                return x
        return default

    async def single(self, query: Optional[Callable[[type[T]], bool]] = None) -> T:
        if query is not None:
            self._new_query(query)

        r = None
        found = False
        async for x in self:
            if self._check(x):
                if found:
                    raise ValueError("More than one element found.")
                r = x
                found = True
        if r is not None:
            return r
        raise ValueError("No element were found.")

    async def single_or_default(
        self, query: Optional[Callable[[type[T]], bool]] = None, default: Any = None
    ) -> Optional[T]:
        if query is not None:
            self._new_query(query)

        r = None
        found = False
        async for x in self:
            if self._check(x):
                if found:
                    raise ValueError("More than one element found.")
                r = x
                found = True
        if r is not None:
            return r
        return default

    async def to_list(self) -> list[T]:
        return [x async for x in self]

    async def to_tuple(self) -> tuple[T, ...]:
        return tuple([x async for x in self])
