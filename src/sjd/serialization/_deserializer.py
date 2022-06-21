from typing import Any, Optional

from ._shared import get_properties, T
from ._serializable import Serializable
from ..entity._property_options import PropertyBinder


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

    if issubclass(entity, Serializable):
        return entity.deserialize(data)

    inputs_map: dict[str, Any] = {}
    dont_inits: list[str] = []
    found_props = 0
    for prop in get_properties(entity):
        j_prop_name = prop.json_property_name or prop.actual_name
        binder: Optional[PropertyBinder] = getattr(prop, "binder", None)
        if binder is not None:
            attribute_name = binder.attribute_name
            attribute_type = binder.attribute_type or prop.type_of_entity
        else:
            attribute_name = prop.actual_name
            attribute_type = prop.type_of_entity
        # if you use binder, it will be everywhere

        if not prop.init:
            dont_inits.append(attribute_name)

        if j_prop_name not in data:
            if prop.required:
                raise ValueError(
                    f"Property '{j_prop_name}' is required but not found in the data."
                )
            if prop.default_factory is not None:
                inputs_map[attribute_name] = prop.default_factory()
            continue

        if prop.is_list:
            inputs_map[attribute_name] = [
                deserialize(attribute_type, x) for x in data[j_prop_name]
            ]
        elif prop.is_complex:
            inputs_map[attribute_name] = deserialize(attribute_type, data[j_prop_name])
        else:
            if isinstance(prop, Serializable):
                inputs_map[attribute_name] = prop.deserialize(data[j_prop_name])
            else:
                inputs_map[attribute_name] = data[j_prop_name]
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
    obj = entity()
    for key, value in inputs_map.items():
        setattr(obj, key, value)
    return obj
