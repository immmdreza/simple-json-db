from typing import Any, Optional

from ._shared import get_properties
from ._serializable import Serializable
from ..entity._property_options import PropertyBinder


def serialize(entity: Any) -> Any:
    """Serialize an entity to a JSON object.

    Args:
        entity (`Any`): The entity to serialize.

    Raises:
        `ValueError`: If the entity is not serializable.

    Returns:
        `Any`: The serialized entity.
    """

    if entity is None:
        return None

    if isinstance(entity, Serializable):
        return entity.serialize()

    result: dict[str, Any] = {}
    found_props = 0
    for prop in get_properties(entity.__class__):
        j_prop_name = prop.json_property_name or prop.actual_name

        binder: Optional[PropertyBinder] = getattr(prop, "binder", None)
        if binder is not None:
            attribute_name = binder.attribute_name
        else:
            attribute_name = prop.actual_name

        if not hasattr(entity, attribute_name):
            if prop.required:
                raise ValueError(
                    f"Property '{attribute_name}' "
                    "is required but not found in the entity."
                )
            if prop.default_factory is not None:
                result[j_prop_name] = prop.default_factory()
            continue

        if prop.is_list:
            result[j_prop_name] = [
                serialize(x) for x in getattr(entity, attribute_name)
            ]
        elif prop.is_complex:
            result[j_prop_name] = serialize(getattr(entity, attribute_name))
        else:
            value = getattr(entity, attribute_name)
            if isinstance(prop, Serializable):
                result[j_prop_name] = prop.serialize_from(value)
            else:
                result[j_prop_name] = value
        found_props += 1

    if found_props == 0:
        if isinstance(entity, (list, tuple)):
            return [serialize(x) for x in entity]  # type: ignore
        return entity
    return result
