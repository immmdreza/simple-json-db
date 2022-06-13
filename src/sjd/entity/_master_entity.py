from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar
import uuid

from ..serialization._shared import T
from ._property import TProperty


_TKey = TypeVar("_TKey", str, int)
_TMasterEntity = TypeVar("_TMasterEntity", bound="MasterEntity")


class MasterEntity(Generic[_TKey, T], ABC):
    """The master of any entity that keeps an entity along with an id."""

    slave_entity_type: type[T]

    __id: TProperty[_TKey]
    """The unique key of the entity."""

    slave: TProperty[T]
    """The slave entity (The master of itself of course)."""

    def __init__(self, slave_entity: Optional[T] = None) -> None:
        self.__id = self.__generate_key__()
        self.slave = slave_entity  # type: ignore

    @property
    def id(self):  # pylint: disable=invalid-name
        """The unique key of the entity."""
        return self.__id

    @classmethod
    def set_id_property(cls: type[_TMasterEntity], id_property: TProperty[_TKey]):
        """Set the id property of the master entity."""
        cls.__id = id_property

    @abstractmethod
    def __generate_key__(self) -> _TKey:
        ...


def _clone_master_entity(base: type[_TMasterEntity]) -> type[_TMasterEntity]:
    class _Result(base):  # type: ignore
        pass

    return _Result


class MasterEntityFactory(Generic[_TMasterEntity, _TKey, T]):
    """A factory for MasterEntity."""

    def __init__(
        self, master_type: type[_TMasterEntity], slave_entity_type: type[T]
    ) -> None:
        """Initialize a new MasterEntityFactory."""

        self._slave_entity_type = slave_entity_type
        self._master_type = _clone_master_entity(master_type)
        self._master_type.slave = TProperty(
            self._slave_entity_type,
            init=True,
            required=True,
            is_complex=True,
            actual_name="_MasterEntity_slave",
            json_property_name="slave",
        )
        self._master_type.set_id_property(self.__get_property__())

    @property
    def master_entity_type(self):
        """The type of the master entity."""
        return self._master_type

    @abstractmethod
    def __get_property__(self) -> TProperty[_TKey]:
        ...

    def __call__(self, entity: T) -> MasterEntity[_TKey, T]:
        return self._master_type(entity)


class UuidMasterEntity(MasterEntity[str, T]):
    """A master entity based on uuid."""

    def __generate_key__(self) -> str:
        return str(uuid.uuid4())


class UuidMasterEntityFactory(MasterEntityFactory[UuidMasterEntity, str, T]):
    """A factory for `UuidMasterEntity`."""

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
