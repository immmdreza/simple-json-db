import inspect
from typing import Any, Generator, TypeVar

from ..entity._property import TProperty


T = TypeVar("T")


def get_properties(entity: type[Any]) -> Generator[TProperty[Any], None, None]:
    """Get all properties of an entity."""
    for _, value in inspect.getmembers(entity):
        if isinstance(value, TProperty):
            yield value
