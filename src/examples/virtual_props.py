import asyncio

from sjd import TEntity, Engine, properties as props


class Grade(TEntity):
    __json_init__ = True

    course_id = props.IntProperty(required=True)
    course_name = props.StrProperty(required=True)
    score = props.IntProperty(required=True)

    student_id = props.ReferenceProperty()

    def __init__(self, course_id: int, course_name: str, score: int):
        self.course_id = course_id
        self.course_name = course_name
        self.score = score


class Student(TEntity):
    __json_init__ = True

    student_id = props.IntProperty(required=True)
    first_name = props.StrProperty(required=True)
    last_name = props.StrProperty()

    grades = props.VirtualListProperty(Grade, "student_id")

    def __init__(
        self,
        student_id: int,
        first_name: str,
        last_name: str,
        grades: list[Grade] = [],
    ):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.grades = grades


class AppEngine(Engine):

    students = Engine.set(Student)
    grades = Engine.set(Grade)

    def __init__(self):
        super().__init__("__test_db__")


async def main():

    engine = AppEngine()

    await engine.students.add(
        Student(1, "Arash", "Eshi", [Grade(1, "Physics", 20)]),
    )

    arash = await engine.students.as_queryable.first(lambda s: s.first_name == "Arash")

    async for grade in engine.students.iter_referenced_by(arash, lambda s: s.grades):
        print(grade.course_name)


if __name__ == "__main__":
    asyncio.run(main())