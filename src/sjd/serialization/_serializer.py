from typing import Any

from ._shared import get_properties


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

    result: dict[str, Any] = {}
    found_props = 0
    for property in get_properties(entity.__class__):
        j_prop_name = property.json_property_name or property.actual_name

        if property.actual_name not in entity.__dict__:
            if property.required:
                raise ValueError(
                    f"Property '{j_prop_name}' is required but not found in the entity."
                )
            else:
                if property.default_factory is not None:
                    result[j_prop_name] = property.default_factory()
                continue

        if property.is_list:
            result[j_prop_name] = [
                serialize(x) for x in getattr(entity, property.actual_name)
            ]
        elif property.is_complex:
            result[j_prop_name] = serialize(getattr(entity, property.actual_name))
        else:
            result[j_prop_name] = getattr(entity, property.actual_name)
        found_props += 1

    if found_props == 0:
        if isinstance(entity, (list, tuple)):
            return [serialize(x) for x in entity]  # type: ignore
        return entity
    return result
