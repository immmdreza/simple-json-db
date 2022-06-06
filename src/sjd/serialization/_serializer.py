from typing import Any

from ._shared import get_properties
from ._serializable import Serializable


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

        if prop.actual_name not in entity.__dict__:
            if prop.required:
                raise ValueError(
                    f"Property '{j_prop_name}' is required but not found in the entity."
                )
            if prop.default_factory is not None:
                result[j_prop_name] = prop.default_factory()
            continue

        if prop.is_list:
            result[j_prop_name] = [
                serialize(x) for x in getattr(entity, prop.actual_name)
            ]
        elif prop.is_complex:
            result[j_prop_name] = serialize(getattr(entity, prop.actual_name))
        else:
            if isinstance(prop, Serializable):
                result[j_prop_name] = prop.serialize()
            else:
                result[j_prop_name] = getattr(entity, prop.actual_name)
        found_props += 1

    if found_props == 0:
        if isinstance(entity, (list, tuple)):
            return [serialize(x) for x in entity]  # type: ignore
        return entity
    return result
