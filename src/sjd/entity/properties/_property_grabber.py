import inspect
import datetime
from types import NoneType
from typing import Any, Callable, Optional

from .._entity import TEntity, EmbeddedEntity
from .._property import TProperty
from ..properties._datetime_property import DateTimeProperty
from ...serialization._shared import T


VALID_TYPES = (  # type: ignore
    str,
    int,
    float,
    bool,
    list,
    TEntity,
    datetime.datetime,
    EmbeddedEntity,
)


def __resolve_type(
    name: str, annotation: Any, optional: bool = False
) -> Optional[tuple[type[Any], bool, bool, bool]]:

    try:
        if issubclass(annotation, VALID_TYPES):
            is_complex = issubclass(annotation, (TEntity, EmbeddedEntity))
            return (annotation, optional, False, is_complex)  # type: ignore
        return None
    except TypeError:
        if hasattr(annotation, "__args__"):
            __args__: tuple[type[Any], ...] = annotation.__args__  # type: ignore
            if len(__args__) == 1:
                if hasattr(annotation, "__origin__"):
                    if annotation.__origin__ is list:  # type: ignore
                        return (__args__[0], optional, True, False)
                    else:
                        return None
                else:
                    return None
            elif len(__args__) == 2:
                try:
                    _ = next(x for x in __args__ if x is NoneType)
                    other_type = next(x for x in __args__ if x is not NoneType)
                    return __resolve_type(name, other_type, optional=True)
                except StopIteration:
                    return None
            else:
                return None
        else:
            return None


def __grab_props(__init__: Callable[..., Any]):
    sign = inspect.signature(__init__)

    if __init__.__name__ != "__init__":
        raise ValueError("Not an __init__ methods.")

    for key, value in sign.parameters.items():
        if key == "self":
            continue
        annotation = value.annotation
        resolved_type = __resolve_type(key, annotation)
        if resolved_type is None:
            continue
        yield key, *resolved_type


def auto_collect(
    *, method_name: str = "__init__", ignore_params: Optional[list[str]] = None
) -> Callable[[type[T]], type[T]]:
    """Automatically collect properties from `__init__` method.

    Note that only valid types are allowed.
    - `str`, `int`, `float`, `bool`, `list`, subclass of (`TEntity`, `EmbedEntity`)
    - `Optional[T]`, where `T` is one of the above
    - `None | T` or `T | None` where T is one of the above

    Remember, attribute names should be the same as parameter names.

    Args:
        Cls (`type[Any]`): Type to collect properties from.
        method_name (`str`): Name of the method to collect properties from.
        ignore_params (`list[str]`): List of parameters to ignore.

    Returns:
        type[`Any`]: Type with properties collected.
    """

    def __collect_them(Cls: type[T], /) -> type[T]:
        if ignore_params is None:
            to_ignore = []
        else:
            to_ignore = ignore_params

        for member in inspect.getmembers(Cls, inspect.isfunction):
            if member[0] == method_name:
                found_any = False
                for info in __grab_props(member[1]):
                    if info[0] in to_ignore:
                        continue

                    if hasattr(Cls, info[0]):
                        continue

                    if info[1] == datetime.datetime:
                        prop = DateTimeProperty(
                            init=True,
                            required=not info[2],
                            json_property_name=info[0],
                            default_factory=lambda: None,
                            actual_name=info[0],
                        )
                    else:
                        prop = TProperty(
                            info[1],
                            init=True,
                            required=not info[2],
                            json_property_name=info[0],
                            is_list=info[3],
                            is_complex=info[4],
                            default_factory=lambda: info[0],  # type: ignore
                            actual_name=info[0],
                        )

                    setattr(Cls, info[0], prop)
                    found_any = True
                if found_any:
                    setattr(Cls, "__json_init__", True)
        return Cls

    return __collect_them
