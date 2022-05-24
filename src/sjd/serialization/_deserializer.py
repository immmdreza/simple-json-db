from typing import Any, Optional
from ._shared import get_properties, T


def deserialize(entity: type[T], data: Any) -> Optional[T]:
    """Deserialize a JSON object into an entity.

    Args:
        entity (`type[T]`): The type of the entity to deserialize to.
        data (`Any`): The JSON object to deserialize.

    Raises:
        `ValueError`: If a required property is missing.

    Returns:
        `T`: The deserialized entity.
    """

    if not data:
        return None

    inputs_map: dict[str, Any] = {}
    dont_inits: list[str] = []
    found_props = 0
    for property in get_properties(entity):
        j_prop_name = property.json_property_name or property.actual_name
        if not property.init:
            dont_inits.append(property.actual_name)

        if j_prop_name not in data:
            if property.required:
                raise ValueError(
                    f"Property '{j_prop_name}' is required but not found in the data."
                )
            else:
                if property.default_factory is not None:
                    inputs_map[property.actual_name] = property.default_factory()
                continue

        if property.is_list:
            inputs_map[property.actual_name] = [
                deserialize(property.type_of_entity, x) for x in data[j_prop_name]
            ]
        elif property.is_complex:
            inputs_map[property.actual_name] = deserialize(
                property.type_of_entity, data[j_prop_name]
            )
        else:
            inputs_map[property.actual_name] = data[j_prop_name]
        found_props += 1

    if found_props == 0:
        if isinstance(data, (list, tuple)):
            return [deserialize(entity, x) for x in data]  # type: ignore
        return data

    should_init = getattr(entity, "__json_init__", None)

    if should_init:
        obj = entity(**{k: v for k, v in inputs_map.items() if k not in dont_inits})
        for dont_init in dont_inits:
            setattr(obj, dont_init, inputs_map[dont_init])
        return obj
    else:
        obj = entity()
        for key, value in inputs_map.items():
            setattr(obj, key, value)
        return obj
