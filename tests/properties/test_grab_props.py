from typing import Optional

from src.sjd import TEntity, EmbeddedEntity
from src.sjd.entity.properties._property_grabber import auto_collect
from src.sjd.serialization import serialize, deserialize


def test_1():
    class Grade(TEntity):
        pass

    class Info(EmbeddedEntity):
        pass

    # Create a model to store.
    @auto_collect()
    class Student(TEntity):  # type: ignore
        def __init__(
            self,
            int_p: int,
            optional_int: Optional[int],
            str_p: str,
            optional_str: str | None,
            bool_p: bool,
            float_p: float,
            optional_float: None | float,
            l_p: list[str],
            c_p: Grade,
            e_p: Info,
            lc_p: list[Grade],
            pc_p: Optional[Grade],
            optional_list: Optional[list[str]],
        ):
            pass


def test_2():
    @auto_collect()
    class Student(TEntity):
        def __init__(self, first_name: str, last_name: str | None = None) -> None:
            super().__init__()
            self.first_name = first_name
            self.last_name = last_name

    student = Student("John", "Doe")

    s = serialize(student)
    d = deserialize(Student, s)

    assert d
    assert d.first_name == "John"
