from enum import Enum
from typing import Generic

from ..serialization._shared import T
from ..serialization import serialize
from ..entity._master_entity import MasterEntity, _TKey


class TrackingMode(Enum):
    UPDATE = "update"
    """Indicates that the entity should be updated."""
    CREATE = "create"
    """Indicates that the entity should be created."""
    DELETE = "delete"
    """Indicates that the entity should be deleted."""


class EntityTracker(Generic[_TKey, T]):
    def __init__(
        self, key: _TKey, master_entity_to_track: MasterEntity[_TKey, T]
    ) -> None:
        self._key: _TKey = key
        self._master_entity: MasterEntity[_TKey, T] = master_entity_to_track
        self._entity_to_track = master_entity_to_track.slave
        self._latest_serialized_data = None
        self._initial_schema = serialize(self._entity_to_track)
        self._tracking_mode = TrackingMode.UPDATE

    @property
    def modified(self) -> bool:
        self._latest_serialized_data = serialize(self._entity_to_track)
        return self._initial_schema != self._latest_serialized_data

    @property
    def key(self) -> _TKey:
        return self._key

    @property
    def entity(self) -> T:
        return self._entity_to_track

    @property
    def latest(self):
        self._latest_serialized_data = serialize(self._entity_to_track)
        return self._latest_serialized_data

    @property
    def tracking_mode(self) -> TrackingMode:
        return self._tracking_mode

    @property
    def master_entity(self) -> MasterEntity[_TKey, T]:
        return self._master_entity

    def set_tracking_mode_delete(self) -> None:
        self._tracking_mode = TrackingMode.DELETE

    def set_tracking_mode_create(self) -> None:
        self._tracking_mode = TrackingMode.CREATE

    def set_tracking_mode_update(self) -> None:
        self._tracking_mode = TrackingMode.UPDATE

    def set_tracking_mode(self, mode: TrackingMode) -> None:
        self._tracking_mode = mode
