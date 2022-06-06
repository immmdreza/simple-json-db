from typing import Optional

from ._complex_property import ComplexProperty, VirtualComplexProperty
from ._optional_property import OptionalProperty
from ._list_property import ListProperty, VirtualListProperty
from ._int_property import IntProperty
from ._str_property import StrProperty, ReferenceProperty
from ._float_property import FloatProperty
from ._bool_property import BoolProperty
from ._datetime_property import DateTimeProperty
from ._property_grabber import auto_collect
from .._property import TProperty
from ...serialization._shared import T


def integer(
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
    """Mark current attribute as an `int` property. ( ClassVar only )"""
    return IntProperty(
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: 0,
    )


def string(
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
    """Mark current attribute as a `str` property. ( ClassVar only )"""
    return StrProperty(
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: "",
    )


def double(
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
    """Mark current attribute as a `float` property. ( ClassVar only )"""
    return FloatProperty(
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: 0.0,
    )


def array(
    of_type: type[T],
    /,
    *,
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
) -> ListProperty[T]:
    """Mark current attribute as a `list` of `T` property. ( ClassVar only )"""
    return ListProperty(
        of_type,
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=list,
    )


def boolean(
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
    """Mark current attribute as a `bool` property. ( ClassVar only )"""
    return BoolProperty(
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: False,
    )


def entity(
    of_type: type[T],
    /,
    *,
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
) -> ComplexProperty[T]:
    """Mark current attribute as an `EmbedEntity` property. ( ClassVar only )"""
    return ComplexProperty(
        of_type,
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: None,
    )


def optional(prop: TProperty[T]) -> TProperty[Optional[T]]:
    """Mark current attribute as an optional `T` property. ( ClassVar only )"""
    if isinstance(prop, OptionalProperty):
        return prop  # type: ignore
    return prop.optional()


def from_entity(
    entity_type: type[T],
    refers_to_property: str,
    *,
    json_property_name: Optional[str] = None,
) -> VirtualComplexProperty[T]:
    """Mark current attribute as a virtual entity that stored in another collection.
    ( ClassVar only )"""

    return VirtualComplexProperty(
        entity_type,
        refers_to_property,
        json_property_name=json_property_name,
    )


def from_entities(
    entity_type: type[T],
    refers_to_property: str,
    *,
    json_property_name: Optional[str] = None,
) -> VirtualListProperty[T]:
    """Mark current attribute as a virtual list of entities that stored
    in another collection. ( ClassVar only )"""

    return VirtualListProperty(
        entity_type,
        refers_to_property,
        json_property_name=json_property_name,
    )


def reference():
    """Mark current attribute as a reference to another entity's id.
    ( ClassVar only )"""

    return ReferenceProperty()


def from_datetime(
    *,
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
    """Represents a placeholder for datetime property."""
    return DateTimeProperty(
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: None,
    )


__all__ = [
    "auto_collect",
    "integer",
    "string",
    "double",
    "array",
    "boolean",
    "entity",
    "optional",
    "from_entity",
    "from_entities",
    "reference",
    "from_datetime",
]
