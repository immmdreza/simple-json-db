from enum import Enum
from typing import Generic

from ..serialization._shared import T
from ..serialization import serialize
from ..entity._master_entity import MasterEntity, _TKey


class TrackingMode(Enum):
    """The mode of tracking."""

    UPDATE = "update"
    """Indicates that the entity should be updated."""
    CREATE = "create"
    """Indicates that the entity should be created."""
    DELETE = "delete"
    """Indicates that the entity should be deleted."""


class _EntityTracker(Generic[_TKey, T]):
    def __init__(
        self, key: _TKey, master_entity_to_track: MasterEntity[_TKey, T]
    ) -> None:
        self._key: _TKey = key
        self._master_entity: MasterEntity[_TKey, T] = master_entity_to_track
        self._entity_to_track = master_entity_to_track.slave
        self._latest_serialized_data = None
        self._initial_schema = serialize(self._entity_to_track)
        self._tracking_mode = TrackingMode.UPDATE

    def replace_entity(self, new_entity: T):
        """Replace slave entity."""
        self._master_entity.slave = new_entity
        self._entity_to_track = new_entity

    @property
    def modified(self) -> bool:
        """Returns True if the entity has been modified."""
        self._latest_serialized_data = serialize(self._entity_to_track)
        return self._initial_schema != self._latest_serialized_data

    @property
    def key(self) -> _TKey:
        """Returns the key of the entity to track."""
        return self._key

    @property
    def entity(self) -> T:
        """Returns the entity to track."""
        return self._entity_to_track

    @property
    def latest(self):
        """Returns the latest serialized data of the entity."""
        self._latest_serialized_data = serialize(self._entity_to_track)
        return self._latest_serialized_data

    @property
    def tracking_mode(self) -> TrackingMode:
        """Returns the tracking mode of the entity."""
        return self._tracking_mode

    @property
    def master_entity(self) -> MasterEntity[_TKey, T]:
        """Returns the master entity to track."""
        return self._master_entity

    def set_tracking_mode_delete(self) -> None:
        """Sets the tracking mode to delete."""
        self._tracking_mode = TrackingMode.DELETE

    def set_tracking_mode_create(self) -> None:
        """Sets the tracking mode to create."""
        self._tracking_mode = TrackingMode.CREATE

    def set_tracking_mode_update(self) -> None:
        """Sets the tracking mode to update."""
        self._tracking_mode = TrackingMode.UPDATE

    def set_tracking_mode(self, mode: TrackingMode) -> None:
        """Sets the tracking mode to the given mode."""
        self._tracking_mode = mode
