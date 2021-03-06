# pylint: skip-file

import asyncio
from pathlib import Path

from sjd import TEntity, EmbeddedEntity, Engine, properties as props


class Grade(EmbeddedEntity):
    __json_init__ = True

    course_id = props.integer(required=True)
    course_name = props.string(required=True)
    score = props.integer(required=True)

    def __init__(self, course_id: int, course_name: str, score: int):
        self.course_id = course_id
        self.course_name = course_name
        self.score = score


class Student(TEntity):
    __json_init__ = True

    student_id = props.string(required=True)
    first_name = props.string(required=True)
    last_name = props.string().optional()
    grades = props.array(Grade)

    def __init__(
        self,
        student_id: int,
        first_name: str,
        last_name: str | None = None,
        grades: list[Grade] = [],
    ):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.grades = grades


class AppEngine(Engine):

    students = Engine.set(Student)

    def __init__(self):
        super().__init__(Path("__test_db__"))


async def main():

    engine = AppEngine()

    engine.students.add_range(
        Student(1, "John", "Doe", [Grade(1, "Math", 90), Grade(2, "English", 80)]),
        Student(2, "Jane", "Doe", [Grade(1, "Math", 90), Grade(2, "English", 80)]),
    )

    await engine.students.save_changes_async()


if __name__ == "__main__":
    asyncio.run(main())
