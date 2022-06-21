import datetime
from typing import Any, Callable, Optional

from .._property import SerializableProperty


class DateTimeProperty(SerializableProperty[datetime.datetime]):
    """Represents a placeholder for datetime property."""

    def __init__(
        self,
        /,
        *,
        init: bool = True,
        required: bool = False,
        json_property_name: Optional[str] = None,
        default_factory: Optional[Callable[[], Optional[datetime.datetime]]] = None,
        actual_name: Optional[str] = None,
    ):
        """Initialize a new instance of DateTimeProperty.

        Args:
            init: Whether the property should be initialized.
            required: Whether the property is required.
            json_property_name: The name of the property in JSON.
            default_factory: A function that returns a default value for the property.
        """

        super().__init__(
            datetime.datetime,
            init=init,
            required=required,
            json_property_name=json_property_name,
            is_list=False,
            is_complex=False,
            default_factory=default_factory,
            actual_name=actual_name,
        )

    @classmethod
    def __serialize_from__(cls, value: datetime.datetime) -> Any:
        return value.isoformat()

    @classmethod
    def __deserialize__(cls, data: Any) -> Optional[datetime.datetime]:
        return datetime.datetime.fromisoformat(data)
