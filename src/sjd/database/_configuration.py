import dataclasses
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar, TYPE_CHECKING

from ..entity._property import TProperty
from ..serialization._shared import T
from ._descriptors import _Collection, _TCol
from ._collection import AbstractCollection

if TYPE_CHECKING:
    from ._engine import Engine

_TEngine = TypeVar("_TEngine", bound="Engine")


class DeleteAction(Enum):
    """The action to be taken when a record is deleted."""

    DELETE_ENTITY = "delete_entity"
    """ Deletes all virtual entities associated with the entity. """
    DELETE_REFERENCE = "delete_reference"
    """ Removes the reference property from the virtual entities. """
    IGNORE = "ignore"
    """ Ignores the virtual entities. """

    @property
    def ignore(self) -> bool:
        """Returns True if the action is to ignore the virtual entities."""
        return self == DeleteAction.IGNORE

    @property
    def delete_reference(self) -> bool:
        """Returns True if the action is to delete the reference property."""
        return self == DeleteAction.DELETE_REFERENCE

    @property
    def delete_entity(self) -> bool:
        """Returns True if the action is to delete the entity."""
        return self == DeleteAction.DELETE_ENTITY


@dataclasses.dataclass(repr=True)
class PropertyConfiguration:
    """Configuration of a property"""

    delete_action: DeleteAction = DeleteAction.IGNORE

    def __init__(self, property_: TProperty[Any]) -> None:
        self._property = property_

    def set_delete_action(self, action: DeleteAction) -> "PropertyConfiguration":
        """Sets the delete action for the property."""
        if not self._property.is_virtual:
            raise ValueError(
                f"Property {self._property.actual_name} is not virtual. "
                f"Only virtual properties can be configured with delete action."
            )
        self.delete_action = action
        return self

    def delete_whole_reference(self) -> "PropertyConfiguration":
        """Indicates if the entity which this property referees to should be deleted
        when current entity is deleted."""
        return self.set_delete_action(DeleteAction.DELETE_ENTITY)

    def delete_reference_prop(self) -> "PropertyConfiguration":
        """Indicates if the reference property should be deleted ( from reference entity )
        when current entity is deleted."""
        return self.set_delete_action(DeleteAction.DELETE_REFERENCE)


@dataclasses.dataclass(repr=True)
class CollectionConfiguration(Generic[T]):
    """Configuration of a collection."""

    def __init__(self, type_of_entity: type[T]) -> None:
        """Initializes the configuration of a collection."""
        self._entity_type = type_of_entity
        self._properties_config: dict[str, PropertyConfiguration] = {}

    def config_property(
        self,
        selector: Callable[[T], Any],
        configure: Callable[[PropertyConfiguration], Any],
    ) -> "CollectionConfiguration[T]":
        """Configures a property of the collection.

        Args:
            selector (`Callable`): The selector of the property.
            configure (`Callable`): The configuration function.
        """
        selected = selector(self._entity_type)  # type: ignore
        if selected is not None:
            if isinstance(selected, TProperty):
                if selected.actual_name in self._properties_config:
                    self._properties_config[selected.actual_name] = configure(
                        self._properties_config[selected.actual_name]
                    )
                else:
                    self._properties_config[selected.actual_name] = configure(
                        PropertyConfiguration(selected)  # type: ignore
                    )
                return self
            else:
                raise ValueError(
                    f"The selector {selector} returned {selected}"
                    " which is not a property."
                )
        raise ValueError(f"The selector {selector} returned None.")

    def get_property_config(
        self, property_name: str
    ) -> Optional[PropertyConfiguration]:
        """Gets the configuration of a property.

        Args:
            property_name (`str`): The name of the property.
        """
        return self._properties_config.get(property_name, None)


@dataclasses.dataclass(repr=True)
class EngineConfiguration(Generic[_TEngine]):
    """This class is used to configure an engine."""

    def __init__(self, type_of_engine: type[_TEngine]) -> None:
        """Initializes the configuration of a collection."""
        self._engine_type = type_of_engine
        self._collection_configs: dict[
            type[Any], CollectionConfiguration[AbstractCollection[Any, Any, Any]]
        ] = {}

    def config_collection(
        self,
        selector: Callable[[_TEngine], AbstractCollection[Any, Any, T]],
        configure: Callable[[CollectionConfiguration[T]], Any],
    ) -> "EngineConfiguration[_TEngine]":
        """Configure a collection that is registered with the engine.

        Args:
            selector (`Callable[[Engine], AbstractCollection[T]]`):
            The selector that returns the collection.
            configure (`Callable[[CollectionConfiguration[T]], Any]`):
            The configuration function.
        """

        col = selector(self._engine_type)  # type: ignore
        if col is not None:
            if isinstance(col, _Collection):
                if col.entity_type in self._collection_configs:
                    self._collection_configs[col.entity_type] = configure(
                        self._collection_configs[col.entity_type]  # type: ignore
                    )
                else:
                    self._collection_configs[col.entity_type] = configure(
                        CollectionConfiguration(col.entity_type)
                    )
                return self
            else:
                raise ValueError(
                    f"The selector {selector} returned {col} which is not a collection."
                )
        raise ValueError(f"The selector {selector} returned None.")

    def get_collection_config(
        self, type_of_entity: type[_TCol]
    ) -> Optional[CollectionConfiguration[AbstractCollection[Any, Any, _TCol]]]:
        """Returns the configuration of a collection.

        Args:
            type_of_entity (`type`): The type of the collection.
        """
        return self._collection_configs.get(type_of_entity, None)
