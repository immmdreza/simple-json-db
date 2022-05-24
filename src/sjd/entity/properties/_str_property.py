from typing import Callable, Generic, Optional

from .._property import TProperty
from ...serialization._shared import T


class StrProperty(TProperty[str]):
    """IntProperty is a property that stores an string value."""

    def __init__(
        self,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
        required: bool = False,
        default_factory: Optional[Callable[[], Optional[str]]] = None,
    ):
        """Initialize a new IntProperty.

        Args:
            json_property_name (`Optional[str]`, optional): The name of the property in the JSON object. Defaults to None.
            required (`bool`, optional): Whether the property is required. Defaults to False.
            default_factory (`Optional[Callable[[], Optional[str]]]`, optional): A function that returns a default value for the property. Defaults to None.
        """

        super().__init__(
            int,
            init=init,
            json_property_name=json_property_name,
            required=required,
            is_list=False,
            is_complex=False,
            default_factory=default_factory,
        )


class ReferenceProperty(Generic[T], TProperty[str]):
    """ReferenceProperty is a property that stores a reference to an entity."""

    def __init__(
        self,
        _refers_to: type[T],
        _bind_to: str,
        /,
        *,
        json_property_name: Optional[str] = None,
        required: bool = False,
        default_factory: Optional[Callable[[], Optional[str]]] = None,
    ):
        super().__init__(
            int,
            init=False,
            json_property_name=json_property_name,
            required=required,
            is_list=False,
            is_complex=False,
            default_factory=default_factory,
        )
        self._refers_to = _refers_to
        self._bind_to = _bind_to

    @property
    def refers_to(self):
        return self._refers_to

    @property
    def bind_to(self):
        return self._bind_to
