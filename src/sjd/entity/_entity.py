from abc import ABC
from typing import Any, ClassVar, Optional
import uuid

from .._._type_alias import JsonObject
from .properties import StrProperty
from ..serialization._serializable import Serializable
from ..serialization._shared import get_properties
from ..serialization._deserializer import deserialize
from ..serialization._serializer import serialize


class TEntity(Serializable, ABC):
    """Abstract template class for all entities."""

    __json_init__: ClassVar[bool] = False
    """ Indicates if the data should be passed to __init__ function. """

    __id = StrProperty(required=True, init=False, json_property_name="__id")

    def __new__(cls, *args: Any, **kwargs: Any):
        obj = object.__new__(cls)
        obj.__id = str(uuid.uuid4())
        return obj

    @property
    def id(self):
        return self.__id

    @classmethod
    def get_properties(cls):
        """
        Get all properties of the entity.
        """
        return get_properties(cls)

    def __serialize__(self) -> JsonObject:
        """
        Serialize the entity.
        """
        return serialize(self)

    @classmethod
    def __deserialize__(cls, data: JsonObject) -> Optional["TEntity"]:
        """
        Deserialize the entity.
        """
        return deserialize(cls, data)


class EmbedEntity(Serializable, ABC):
    """Abstract template class for embed entities."""

    __json_init__: ClassVar[bool] = False
    """ Indicates if the data should be passed to __init__ function. """

    @classmethod
    def get_properties(cls):
        """
        Get all properties of the entity.
        """
        return get_properties(cls)

    def __serialize__(self) -> JsonObject:
        """
        Serialize the entity.
        """
        return serialize(self)

    @classmethod
    def __deserialize__(cls, data: JsonObject):
        """
        Deserialize the entity.
        """
        return deserialize(cls, data)
