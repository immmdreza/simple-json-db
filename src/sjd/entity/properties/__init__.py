from typing import Optional

from ._complex_property import ComplexProperty, VirtualComplexProperty
from ._optional_property import OptionalProperty
from ._list_property import ListProperty, VirtualListProperty
from ._int_property import IntProperty
from ._str_property import StrProperty, ReferenceProperty
from ._float_property import FloatProperty
from ._bool_property import BoolProperty
from ._property_grabber import auto_collect
from .._property import TProperty
from ...serialization._shared import T


def integer(
    init: bool = True,
    json_property_name: Optional[str] = None,
    required: bool = False,
):
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
    return ComplexProperty(
        of_type,
        init=init,
        json_property_name=json_property_name,
        required=required,
        default_factory=lambda: None,
    )


def optional(property: TProperty[T]) -> OptionalProperty[T]:
    if isinstance(property, OptionalProperty):
        return property  # type: ignore

    if property.required:
        raise ValueError("Cannot create an optional property from a required property.")

    return OptionalProperty(
        property.type_of_entity,
        init=property.init,
        default_factory=lambda: None,
        is_list=property.is_list,
        json_property_name=property.json_property_name,
        is_complex=property.is_complex,
    )


def from_entity(
    entity_type: type[T],
    refers_to_property: str,
    *,
    json_property_name: Optional[str] = None,
) -> VirtualComplexProperty[T]:
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
    return VirtualListProperty(
        entity_type,
        refers_to_property,
        json_property_name=json_property_name,
    )


def reference():
    return ReferenceProperty()


__all__ = [
    "collect_props_from_init",
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
]
