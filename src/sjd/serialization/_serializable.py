from abc import ABC, abstractmethod
from typing import Any


class Serializable(ABC):
    """
    Abstract template class for all serializable entities.
    """

    @abstractmethod
    def __serialize__(self) -> Any:
        """
        Serialize the entity.
        """
        ...

    def serialize(self):
        return self.__serialize__()

    @classmethod
    @abstractmethod
    def __deserialize__(cls, data: Any) -> Any:
        """
        Deserialize the entity.
        """
        ...
