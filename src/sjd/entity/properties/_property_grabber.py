import inspect
from types import NoneType
from typing import Any, Callable, NoReturn

from .._entity import TEntity, EmbedEntity, TProperty
from ...serialization._shared import T


VALID_TYPES = (  # type: ignore
    str,
    int,
    float,
    bool,
    list,
    TEntity,
    EmbedEntity,
)


def __resolve_type(
    name: str, annotation: Any, optional: bool = False
) -> tuple[type[Any], bool, bool, bool]:
    def __raise() -> NoReturn:
        raise ValueError(f"Parameter {name} has invalid type: {annotation}")

    try:
        if issubclass(annotation, VALID_TYPES):
            is_complex = issubclass(annotation, (TEntity, EmbedEntity))
            return (annotation, optional, False, is_complex)  # type: ignore
        __raise()
    except TypeError:
        if hasattr(annotation, "__args__"):
            __args__: tuple[type[Any], ...] = annotation.__args__  # type: ignore
            if len(__args__) == 1:
                if hasattr(annotation, "__origin__"):
                    if annotation.__origin__ is list:  # type: ignore
                        return (__args__[0], optional, True, False)
                    else:
                        __raise()
                else:
                    __raise()
            elif len(__args__) == 2:
                try:
                    _ = next(x for x in __args__ if x is NoneType)
                    other_type = next(x for x in __args__ if x is not NoneType)
                    return __resolve_type(name, other_type, optional=True)
                except StopIteration:
                    __raise()
            else:
                __raise()
        else:
            __raise()


def __grab_props(__init__: Callable[..., Any]):
    sign = inspect.signature(__init__)

    if __init__.__name__ != "__init__":
        raise ValueError("Not an __init__ methods.")

    for k, v in sign.parameters.items():
        if k == "self":
            continue
        annotation = v.annotation
        yield k, *__resolve_type(k, annotation)


def collect_props_from_init(Cls: type[T], /) -> type[T]:
    """Automatically collect properties from `__init__` method.

    Note that only valid types are allowed.
    - `str`, `int`, `float`, `bool`, `list`, subclass of (`TEntity`, `EmbedEntity`)
    - `Optional[T]`, where `T` is one of the above
    - `None | T` or `T | None` where T is one of the above

    Remember, attribute names should be the same as parameter names.

    Args:
        Cls (`type[Any]`): Type to collect properties from.

    Returns:
        type[`Any`]: Type with properties collected.
    """

    for member in inspect.getmembers(Cls, inspect.isfunction):
        if member[0] == "__init__":
            found_any = False
            for info in __grab_props(member[1]):
                setattr(
                    Cls,
                    info[0],
                    TProperty(
                        info[1],
                        init=True,
                        required=not info[2],
                        json_property_name=info[0],
                        is_list=info[3],
                        is_complex=info[4],
                        default_factory=info[0],  # type: ignore
                        actual_name=info[0],
                    ),
                )
                found_any = True
            if found_any:
                setattr(Cls, "__json_init__", True)
    return Cls
