# pylint: skip-file

import asyncio
from typing import Optional
from uuid import uuid4

from sjd import TEntity, Engine, properties as props, make_property, PropertyOptions


@props.auto_collect()
class Student(TEntity):
    def __init__(self, first_name: str, last_name: Optional[str] = None):
        self.first_name = first_name
        self.last_name = last_name
        self._private_key = str(uuid4())

    @make_property(
        str, options=PropertyOptions(init=False, required=True), binder="_private_key"
    )
    def private_key(self):
        # private_key is an actual property
        # Unless you dont define a setter, it's impossible to set value for it.
        return self._private_key

    @private_key.setter  # You can optionally define a setter or even deleter ...
    def private_key(self, _):
        raise AttributeError(
            "Attribute private_key can't be set after it's initialized"
        )


class AppEngine(Engine):
    __db_path__ = "__test_db__"
    students = Engine.set(Student)


async def main():

    engine = AppEngine()
    students_col = engine.students

    students_col.add_range(
        Student("Johhny", "Deep"),
        Student("Jececa", "Doe"),
        Student("Jack", "Makron"),
    )

    await engine.save_changes_async()

    async for student in students_col:
        print(student.private_key)
        # a77d0534-f09f-4977-81d7-55a0373155bc
        student.private_key = "My new blah"
        # AttributeError: Attribute private_key can't be set after it's initialized


if __name__ == "__main__":
    asyncio.run(main())
