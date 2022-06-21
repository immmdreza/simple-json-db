from typing import Any, Callable, Generic, Optional, overload

from ._property_options import PropertyOptions, PropertyBinder
from ._property import TProperty, T


class AdvProperty(Generic[T], property, TProperty[T]):
    """A copy of `TProperty` which is a real property!
    enabling you to define custom getter, setter or deleter."""

    def __init__(
        self,
        type_of_entity: type[Any],
        options: Optional[PropertyOptions[Any]] = None,
        fget: Callable[[Any], T] | None = None,
        fset: Callable[[Any, T], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
        binder: Optional[PropertyBinder | str] = None,
    ):
        if options is None:
            raise ValueError("Options should not be None.")

        super().__init__(fget, fset, fdel, doc)

        self._options = options

        self._init = options.init
        self._required = options.required
        self._type_of_entity = type_of_entity
        self._json_property_name = options.json_property_name
        self._is_list: bool = options.is_list
        self._is_complex: bool = options.is_complex
        self._default_factory = options.default_factory
        self._actual_name = options.actual_name

        if binder is not None:
            if isinstance(binder, str):
                binder = PropertyBinder(binder)

        self._binder = binder

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._actual_name = name
        self._options.actual_name = name

    def setter(self, fset):
        prop = type(self)(
            self._type_of_entity,
            self._options,
            self.fget,
            fset,
            self.fdel,
            self.__doc__,
            self.binder,
        )
        return prop

    def getter(self, fget):
        prop = type(self)(
            self._type_of_entity,
            self._options,
            fget,
            self.fset,
            self.fdel,
            self.__doc__,
            self.binder,
        )
        return prop

    def deleter(self, fdel):
        prop = type(self)(
            self._type_of_entity,
            self._options,
            self.fget,
            self.fset,
            fdel,
            self.__doc__,
            self.binder,
        )
        return prop

    @property
    def binder(self) -> Optional[PropertyBinder]:
        """Indicates if the value should be transferred from another attribute."""
        return self._binder


@overload
def make_property(
    __type_of_entity: type[Any],
    /,
    *,
    options: Optional[PropertyOptions[T]] = None,
    binder: Optional[PropertyBinder] = None,
) -> Callable[..., AdvProperty[T]]:
    """Make actual properties that we're going to deal with."""


@overload
def make_property(
    __type_of_entity: type[Any],
    /,
    *,
    options: Optional[PropertyOptions[T]] = None,
    binder: str | None = None,
) -> Callable[..., AdvProperty[T]]:
    """Make actual properties that we're going to deal with."""


def make_property(
    __type_of_entity: type[Any],
    /,
    *,
    options: Optional[PropertyOptions[T]] = None,
    binder: Optional[PropertyBinder | str] = None,
) -> Callable[..., AdvProperty[T]]:
    """Make actual properties that we're going to deal with."""

    if options is None:
        options = PropertyOptions()

    def _wrapper(
        fget: Callable[[Any], T] | None = None,
        fset: Callable[[Any, T], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
    ):
        return AdvProperty[T](
            type_of_entity=__type_of_entity,
            options=options,
            fget=fget,
            fset=fset,
            fdel=fdel,
            doc=doc,
            binder=binder,
        )

    return _wrapper
