# pylint: skip-file

import asyncio
from typing import Optional

from sjd import TEntity, Engine, properties as props


@props.auto_collect()
class Student(TEntity):
    def __init__(self, first_name: str, last_name: Optional[str] = None):
        self.first_name = first_name
        self.last_name = last_name


class AppEngine(Engine):
    __db_path__ = "__test_db__"
    students = Engine.set(Student)


async def main():

    engine = AppEngine()

    async with engine.students as students:
        students.add_range(Student("John", "Doe"), Student("Jane", "Doe"))

    async for student in engine.students:
        print(student.first_name, student.last_name)


if __name__ == "__main__":
    asyncio.run(main())
