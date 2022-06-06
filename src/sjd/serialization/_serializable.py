from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, final


_T = TypeVar("_T")


class Serializable(Generic[_T], ABC):
    """
    Abstract template class for all serializable entities.
    """

    @abstractmethod
    def __serialize__(self) -> Any:
        """
        Serialize the entity.
        """

    @classmethod
    @abstractmethod
    def __deserialize__(cls, data: Any) -> Optional[_T]:
        """
        Deserialize the entity.
        """

    @final
    def serialize(self):
        """Serialize the entity."""
        return self.__serialize__()

    @final
    @classmethod
    def deserialize(cls, data: Any) -> Optional[_T]:
        """Deserialize the data into entity of this type."""
        return cls.__deserialize__(data)
