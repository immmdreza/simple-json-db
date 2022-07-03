from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, final


_T = TypeVar("_T")


class Serializable(Generic[_T], ABC):
    """
    Abstract template class for all serializable entities.
    """

    @classmethod
    @abstractmethod
    def __serialize_from__(cls, value: _T) -> Any:
        ...

    def __serialize__(self) -> Any:
        """
        Serialize the entity.
        """
        return self.__serialize_from__(self)  # type: ignore

    @classmethod
    @abstractmethod
    def __deserialize__(cls, data: Any) -> Optional[_T]:
        ...

    @final
    def serialize(self):
        """Serialize the entity."""
        return self.__serialize__()

    @classmethod
    def serialize_from(cls, value: _T) -> Any:
        """Serialize from out of instance."""
        return cls.__serialize_from__(value)

    @final
    @classmethod
    def deserialize(cls, data: Any) -> Optional[_T]:
        """Deserialize the data into entity of this type."""
        return cls.__deserialize__(data)
