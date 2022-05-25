from typing import Callable, Generic, Optional

from .._property import TProperty
from ...serialization._shared import T


class ListProperty(Generic[T], TProperty[list[T]]):
    """ListProperty is a property that stores a list of values."""

    def __init__(
        self,
        _type_of_entity: type[T],
        /,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
        required: bool = False,
        default_factory: Optional[Callable[[], Optional[list[T]]]] = None,
    ):
        """Initialize a new ListProperty.

        Args:
            _type_of_entity (`type[T]`): The type of the entity that is stored in each element of the property.
            json_property_name (`Optional[str]`, optional): The name of the property in the JSON object. Defaults to None.
            required (`bool`, optional): Whether the property is required. Defaults to False.
            default_factory (`Optional[Callable[[], Optional[list[T]]]]`, optional): A function that returns a default value for the property. Defaults to None.
        """

        super().__init__(
            _type_of_entity,
            init=init,
            json_property_name=json_property_name,
            required=required,
            is_list=True,
            is_complex=False,
            default_factory=default_factory,
        )


class VirtualListProperty(Generic[T], TProperty[Optional[list[T]]]):
    """VirtualListProperty is a property that stores a list value which can be loaded lazily."""

    __virtual__ = True
    """Indicates that this class is a virtual property ( Lazy loader )."""

    def __init__(
        self,
        _type_of_entity: type[T],
        _refers_to: str,
        /,
        *,
        json_property_name: Optional[str] = None,
    ):

        super().__init__(
            _type_of_entity,
            init=False,
            json_property_name=json_property_name,
            required=False,
            is_list=True,
            is_complex=False,
            default_factory=list,
        )
        self._refers_to = _refers_to

    @property
    def refers_to(self):
        return self._refers_to
