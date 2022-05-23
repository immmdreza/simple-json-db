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
