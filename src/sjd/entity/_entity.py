from abc import ABC
import inspect
from typing import Any, ClassVar, Generator, final

from ._property import TProperty


def _get_properties(entity: type[Any]) -> Generator[TProperty[Any], None, None]:
    """Get all properties of an entity."""
    for _, value in inspect.getmembers(entity):
        if isinstance(value, TProperty):
            yield value


class TEntity(ABC):
    """Abstract template class for all entities."""

    __json_init__: ClassVar[bool] = False
    """ Indicates if the data should be passed to __init__ function. """

    @final
    @classmethod
    def get_properties(cls):
        """
        Get all properties of the entity.
        """
        return _get_properties(cls)


class EmbeddedEntity(ABC):
    """Abstract template class for embed entities."""

    __json_init__: ClassVar[bool] = False
    """ Indicates if the data should be passed to __init__ function. """

    @classmethod
    def get_properties(cls):
        """
        Get all properties of the entity.
        """
        return _get_properties(cls)
