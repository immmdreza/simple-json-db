from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar


_T = TypeVar("_T")


@dataclass(slots=True)
class PropertyOptions(Generic[_T]):
    """Provide options for a property."""

    init: bool = True
    required: bool = False
    json_property_name: Optional[str] = None
    is_list: bool = False
    is_complex: bool = False
    default_factory: Optional[Callable[[], Optional[_T]]] = None
    actual_name: Optional[str] = None
