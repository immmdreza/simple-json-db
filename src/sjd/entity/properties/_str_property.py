from typing import Callable, Optional

from .._property import TProperty


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


class ReferenceProperty(TProperty[str]):
    """ReferenceProperty is a property that stores a reference to an entity."""

    def __init__(self, /):
        super().__init__(
            int,
            init=False,
            json_property_name=None,
            required=False,
            is_list=False,
            is_complex=False,
            default_factory=lambda: None,
        )
