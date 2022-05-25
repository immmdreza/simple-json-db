"""
Contains stuff related to serialization and deserialization of JSON object.

You can directly import methods `serialize`, `deserialize`, and `get_properties`.
Other methods are considered as private.
"""

from ._deserializer import deserialize
from ._serializer import serialize
from ._shared import get_properties


__all__ = ["serialize", "deserialize", "get_properties"]
