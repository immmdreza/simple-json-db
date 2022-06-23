from abc import ABC
import inspect
from typing import TYPE_CHECKING, Any, ClassVar, Generator, TypeVar, final

from ._property import TProperty

if TYPE_CHECKING:
    from ..database._collection import AbstractCollection
    from ..database._entity_tracker import _EntityTracker


_T = TypeVar("_T")


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

    def __rshift__(
        self: _T, other: "AbstractCollection[Any, Any, _T]"
    ) -> "_EntityTracker[Any, _T]":
        if hasattr(other, "entity_type"):
            if isinstance(self, other.entity_type):
                return other.add(self)
        raise TypeError(f"Entity cannot be added to collection of type {type(other)}.")

    def __lshift__(
        self: _T, other: "AbstractCollection[Any, Any, _T]"
    ) -> "_EntityTracker[Any, _T]":
        if hasattr(other, "entity_type"):
            if isinstance(self, other.entity_type):
                return other.delete(self)
        raise TypeError(f"Entity cannot be added to collection of type {type(other)}.")

    def __ilshift__(self, _):
        raise NotImplementedError
        
    def __irshift__(self, _):
        raise NotImplementedError

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
