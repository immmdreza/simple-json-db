from typing import Callable, Generic
from ..serialization._shared import T


class Query(Generic[T]):
    def __init__(self, query: Callable[[type[T]], bool]) -> None:
        self._query = query

    def check(self, against: T):
        """Check the query against an object.

        Args:
            against (`T`): The object to check.

        Returns:
            `bool`: True if the object is valid against the query
        """

        return self._query(against)  # type: ignore
