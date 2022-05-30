from abc import ABC
from typing import Any, Callable, Generic, Optional, TypeVar, overload, cast


T = TypeVar("T")
"""Supports all types of entities that are supported in JSON."""


class TProperty(Generic[T], ABC):
    """
    Abstract template class for all properties.
    """

    def __init__(
        self,
        _type_of_entity: type[Any],
        /,
        *,
        init: bool = True,
        required: bool = False,
        json_property_name: Optional[str] = None,
        is_list: bool = False,
        is_complex: bool = False,
        default_factory: Optional[Callable[[], Optional[T]]] = None,
        actual_name: Optional[str] = None,
    ):
        """Initialize a new TProperty.

        Args:
            _type_of_entity (`type[Any]`): The type of the entity that is stored in the property.
            required (`bool`, optional): Whether the property is required. Defaults to False.
            json_property_name (`Optional[str]`, optional): The name of the property in the JSON object. Defaults to None.
            is_list (`bool`, optional): Whether the property is a list. Defaults to False.
            is_complex (`bool`, optional): Whether the property is a complex value. Defaults to False.
            default_factory (`Optional[Callable[[], Optional[T]]]`, optional): A function that returns a default value for the property. Defaults to None.
        """

        self._init = init
        self._required = required
        self._type_of_entity = _type_of_entity
        self._json_property_name = json_property_name
        self._is_list: bool = is_list
        self._is_complex: bool = is_complex
        self._default_factory = default_factory
        self._access_trail: tuple[str, ...]
        self._actual_name = actual_name

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._actual_name = name

    @overload
    def __get__(self, obj: None, objtype: None) -> "TProperty[T]":
        ...

    @overload
    def __get__(self, obj: object, objtype: type[object]) -> T:
        ...

    def __get__(
        self, obj: object | None, objtype: type[object] | None = None
    ) -> "TProperty[T]" | T:
        if obj is None:
            return self

        if self._actual_name is None:
            raise AttributeError(
                "Attribute is not initialized! Did you missed __init__ or super().__init__ inside it?"
            )

        return cast(T, obj.__dict__[self._actual_name])

    def __set__(self, obj: object, value: T) -> None:

        if self._actual_name is None:
            raise AttributeError(
                "Attribute is not initialized! Did you missed __init__ or super().__init__ inside it?"
            )

        obj.__dict__[self._actual_name] = value

    def __delete__(self, obj: object) -> None:

        if self._actual_name is None:
            raise AttributeError(
                "Attribute is not initialized! Did you missed __init__ or super().__init__ inside it?"
            )

        del obj.__dict__[self._actual_name]

    def update_access_trail(self, *names: str) -> None:
        self._access_trail = names

    @property
    def init(self):
        return self._init

    @property
    def json_property_name(self) -> Optional[str]:
        """The name of the property in the JSON object."""
        return self._json_property_name

    @property
    def required(self) -> bool:
        """Whether the property is required."""
        return self._required

    @property
    def actual_name(self) -> str:
        """The name of the property in the Python object."""

        if self._actual_name is None:
            raise AttributeError(
                "Attribute is not initialized! Did you missed __init__ or super().__init__ inside it?"
            )

        return self._actual_name

    @property
    def type_of_entity(self) -> type[Any]:
        """The type of the entity that is stored in the property."""
        return self._type_of_entity

    @property
    def is_list(self) -> bool:
        """Whether the property is a list."""
        return self._is_list

    @property
    def is_complex(self) -> bool:
        """Whether the property is a complex value."""
        return self._is_complex

    @property
    def default_factory(self) -> Optional[Callable[[], Optional[T]]]:
        """A function that returns a default value for the property."""
        return self._default_factory

    @property
    def is_virtual(self) -> bool:
        """Whether the property is virtual."""
        return getattr(self, "__virtual__", False)

    def optional(self):
        """Returns a clone of the property with the required flag set to False and hints as optional."""

        if self.required:
            raise ValueError(
                "Cannot create an optional property from a required property."
            )

        return TProperty[Optional[T]](
            self.type_of_entity,
            init=self.init,
            required=False,
            default_factory=lambda: None,
            is_list=self.is_list,
            json_property_name=self.json_property_name,
            is_complex=self.is_complex,
        )
