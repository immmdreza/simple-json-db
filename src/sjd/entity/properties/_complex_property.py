from typing import Callable, Generic, Optional
from .._property import TProperty
from ...serialization._shared import T


class ComplexProperty(Generic[T], TProperty[T]):
    """ComplexProperty is a property that stores a complex value."""

    def __init__(
        self,
        _type_of_entity: type[T],
        /,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
        required: bool = False,
        default_factory: Optional[Callable[[], Optional[T]]] = None,
    ):
        """Initialize a new ComplexProperty.

        Args:
            _type_of_entity (`type[T]`): The type of the entity that is stored in the property.
            json_property_name (`Optional[str]`, optional): The name of the property in the JSON object. Defaults to None.
            required (`bool`, optional): Whether the property is required. Defaults to False.
            default_factory (`Optional[Callable[[], Optional[T]]]`, optional): A function that returns a default value for the property. Defaults to None.
        """

        super().__init__(
            _type_of_entity,
            init=init,
            json_property_name=json_property_name,
            is_list=False,
            is_complex=True,
            required=required,
            default_factory=default_factory,
        )


class OptionalComplexProperty(Generic[T], TProperty[Optional[T]]):
    """OptionalComplexProperty is a property that stores a complex value which is not required."""

    def __init__(
        self,
        _type_of_entity: type[T],
        /,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
    ):
        """Initialize a new ComplexProperty.

        Args:
            _type_of_entity (`type[T]`): The type of the entity that is stored in the property.
            init (`bool`, optional): Whether the property should passed to __init__. Defaults to True.
            json_property_name (`Optional[str]`, optional): The name of the property in the JSON object. Defaults to None.
        """

        super().__init__(
            _type_of_entity,
            init=init,
            json_property_name=json_property_name,
            is_list=False,
            is_complex=True,
            required=False,
            default_factory=lambda: None,
        )


class VirtualComplexProperty(Generic[T], OptionalComplexProperty[T]):
    """VirtualComplexProperty is a property that stores a complex value which can be loaded lazily."""

    __virtual__ = True
    """Indicates that this class is a virtual property ( Lazy loader )."""

    def __init__(
        self,
        _type_of_entity: type[T],
        /,
        *,
        init: bool = True,
        json_property_name: Optional[str] = None,
    ):
        super().__init__(
            _type_of_entity, init=init, json_property_name=json_property_name
        )
