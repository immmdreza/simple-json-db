from typing import Callable, Optional

from .._property import TProperty
from ...serialization._shared import T


class OptionalProperty(TProperty[Optional[T]]):
    """A property that is optional (`required=False`)."""

    def __init__(
        self,
        _type_of_entity: type[T],
        /,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
        is_list: bool = False,
        is_complex: bool = False,
        default_factory: Optional[Callable[[], Optional[T]]] = None,
    ):
        """A property that is optional (required=False).

        Args:
            _type_of_entity (`type[T]`): The type of the entity that this property belongs to.
            init (`bool`, optional): Whether this property should be initialized when the entity is created. Defaults to True.
            json_property_name (`Optional[str]`, optional): The name of the property in JSON. Defaults to None.
            is_list (`bool`, optional): Whether this property is a list. Defaults to False.
            is_complex (`bool`, optional): Whether this property is a complex object. Defaults to False.
            default_factory (`Optional[Callable[[], Optional[T]]]`, optional): A function that returns the default value of this property. Defaults to None.
        """

        super().__init__(
            _type_of_entity,
            init=init,
            required=False,
            json_property_name=json_property_name,
            is_list=is_list,
            is_complex=is_complex,
            default_factory=default_factory,
        )
