from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar
import uuid

from ..serialization import serialize, deserialize
from ..serialization._shared import T
from ..serialization._serializable import Serializable
from ._property import TProperty


_TKey = TypeVar("_TKey", str, int)
_TMasterEntity = TypeVar("_TMasterEntity", bound="MasterEntity")


class MasterEntity(Generic[_TKey, T], Serializable, ABC):

    slave_entity_type: type[T]

    __id: TProperty[_TKey]
    """The unique key of the entity."""

    slave: TProperty[T]
    """The slave entity (The master of itself of course)."""

    def __init__(self, slave_entity: Optional[T] = None) -> None:
        self.__id = self.__generate_key__()
        self.slave = slave_entity  # type: ignore

    def __serialize__(self) -> Any:
        return serialize(self)

    @property
    def id(self):
        return self.__id

    @classmethod
    def __deserialize__(
        cls: type[_TMasterEntity], data: Any
    ) -> Optional[_TMasterEntity]:
        return deserialize(cls, data)

    def change_id(self, new_id: _TKey) -> None:
        self.__id = new_id

    @abstractmethod
    def __generate_key__(self) -> _TKey:
        ...


def get_master_entity_clone(Base: type[_TMasterEntity]) -> type[_TMasterEntity]:
    class __Result(Base):  # type: ignore
        pass

    return __Result


class MasterEntityFactory(Generic[_TMasterEntity, _TKey, T]):
    def __init__(
        self, master_type: type[_TMasterEntity], slave_entity_type: type[T]
    ) -> None:
        self._slave_entity_type = slave_entity_type
        self._master_type = get_master_entity_clone(master_type)
        self._master_type.slave = TProperty(
            self._slave_entity_type,
            init=True,
            required=True,
            is_complex=True,
            actual_name="_MasterEntity_slave",
            json_property_name="slave",
        )
        self._master_type.__id = self.__get_property__()

    @property
    def master_entity_type(self):
        return self._master_type

    @abstractmethod
    def __get_property__(self) -> TProperty[_TKey]:
        ...

    def __call__(self, entity: T) -> MasterEntity[_TKey, T]:
        return self._master_type(entity)


class UuidMasterEntity(MasterEntity[str, T]):
    def __init__(self, slave_entity: Optional[T] = None) -> None:
        super().__init__(slave_entity)

    def __generate_key__(self) -> str:
        return str(uuid.uuid4())


class UuidMasterEntityFactory(MasterEntityFactory[UuidMasterEntity, str, T]):
    def __init__(self, slave_entity_type: type[T]) -> None:
        super().__init__(UuidMasterEntity, slave_entity_type)

    def __get_property__(self) -> TProperty[str]:
        return TProperty(
            str,
            init=False,
            required=True,
            actual_name="_MasterEntity__id",
            json_property_name="__id",
        )
