from abc import ABC, abstractmethod
from typing import AsyncGenerator, Callable, Generic, Optional, TypeVar, cast
from collections.abc import AsyncIterable

from ..serialization._shared import T
from ._query import Query


class _Queryable(Generic[T]):
    def __init__(self) -> None:
        self._queries: list[Query[T]] = []

    def _new_query(self, query: Optional[Callable[[T], bool]]):
        if query is not None:
            self._queries.append(Query(query))
        return self

    def _check(self, against: Optional[T]) -> bool:
        if against is None:
            return False
        return all(q.check(against) for q in self._queries)

    def where(self, query: Callable[[T], bool]):
        """Add a filter to the query.

        Args:
            query (`Callable[[T], bool]`): A function that takes an object and
            returns a boolean.
        """
        return self._new_query(query)

    def clear_filters(self):
        """Remove all filters from the query."""
        self._queries = []


_T = TypeVar("_T", int, float, str, list)


class AbstractAsyncQueryable(_Queryable[T], Generic[T], AsyncIterable[T], ABC):
    """An abstract base class for queryable collections."""

    @abstractmethod
    def __aiter__(self) -> AsyncGenerator[T, None]:
        ...

    async def any_async(self, query: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns True if any element in the sequence satisfies the condition
        in the predicate, otherwise False.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        async for item in self:
            if self._check(item):
                return True
        return False

    async def all_async(self, query: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns True if all elements in the sequence satisfy the condition
        in the predicate, otherwise False.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        async for item in self:
            if not self._check(item):
                return False
        return True

    async def first_async(self, query: Optional[Callable[[T], bool]] = None) -> T:
        """Returns the first element in a sequence that satisfies a specified condition.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        async for item in self:
            if self._check(item):
                return item

        raise StopIteration()

    async def first_or_default_async(
        self, query: Optional[Callable[[T], bool]] = None, default: Optional[T] = None
    ) -> Optional[T]:
        """Returns the first element in a sequence that satisfies a specified
        condition or a default value if no such element is found.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
            default (`Optional[T]`): The default value.
        """
        self._new_query(query)

        async for item in self:
            if self._check(item):
                return item
        return default

    async def single_async(self, query: Optional[Callable[[T], bool]] = None) -> T:
        """Returns the only element of a sequence that satisfies a specified condition,
        and throws an exception if more than one such element exists.


        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        result = None
        found = False
        async for item in self:
            if self._check(item):
                if found:
                    raise ValueError("More than one element found.")
                result = item
                found = True
        if result is not None:
            return result
        raise ValueError("No element were found.")

    async def single_or_default_async(
        self, query: Optional[Callable[[T], bool]] = None, default: Optional[T] = None
    ) -> Optional[T]:
        """Returns the only element of a sequence that satisfies a specified
        condition or a default value if no such element is found.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
            default (`Optional[T]`): The default value.
        """
        self._new_query(query)

        result = None
        found = False
        async for item in self:
            if self._check(item):
                if found:
                    raise ValueError("More than one element found.")
                result = item
                found = True
        if result is not None:
            return result
        return default

    async def to_list_async(self) -> list[T]:
        """Converts the sequence to a list."""
        return [x async for x in self]

    async def to_tuple_async(self) -> tuple[T, ...]:
        """Converts the sequence to a tuple."""
        return tuple([x async for x in self])

    async def count_async(self, query: Optional[Callable[[T], bool]] = None) -> int:
        """Returns the number of elements in a sequence that satisfy a condition.

        Args:
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        count = 0
        async for item in self:
            if self._check(item):
                count += 1
        return count

    async def reduce_async(
        self,
        selector: Callable[[T], _T],
        func: Callable[[_T, _T], _T],
        initial: Optional[_T] = None,
        query: Optional[Callable[[T], bool]] = None,
    ) -> _T:
        """Reduces the sequence to a single value by calling a function on
        each element in the sequence and passing the previous result and the current
        element to the function.

        Args:
            selector (`Callable[[T], _T]`): The selector.
            func (`Callable[[_T, _T], _T]`): The function.
            initial (`Optional[_T]`): The initial value.
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        self._new_query(query)

        result = initial
        async for item in self:
            if result is None:
                result = selector(item)
            else:
                result = func(result, selector(item))
        return cast(_T, result)

    async def sum_by_async(
        self,
        selector: Callable[[T], _T],
        initial: Optional[_T] = None,
        query: Optional[Callable[[T], bool]] = None,
    ) -> _T:
        """Returns the sum of the elements in a sequence.

        Args:
            selector (`Callable[[T], _T]`): The selector.
            initial (`Optional[_T]`): The initial value.
            query (`Optional[Callable[[T], bool]]`): The predicate.
        """
        return await self.reduce_async(selector, lambda x, y: x + y, initial, query)


class AsyncQueryable(Generic[T], AbstractAsyncQueryable[T]):
    """An async queryable."""

    def __init__(self, _iterator: AsyncIterable[T], /) -> None:
        """Initializes a new instance of the AsyncQueryable class.

        Args:
            _iterator (`AsyncIterable[T]`): The iterator.
        """
        super().__init__()
        self._iterator = _iterator

    async def __aiter__(  # pylint: disable=invalid-overridden-method
        self,
    ) -> AsyncGenerator[T, None]:
        async for item in self._iterator:
            yield item
