import asyncio

from sjd import Engine, Collection, TEntity, properties


@properties.auto_collect()
class Student(TEntity):
    def __init__(self, first_name: str) -> None:
        self.first_name = first_name


class StudentsCollection(Collection[Student]):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine, Student, "studentsCollection")

    async def add_student(self, first_name: str):
        self.add(Student(first_name))
        await self.save_changes_async()


class AppEngine(Engine):

    students = Engine.typed_set(Student, StudentsCollection)

    def __init__(self):
        super().__init__("app_engine")


async def main():

    engine = AppEngine()

    await engine.students.add_student("John")
    await engine.students.add_student("Johnny")
    await engine.students.add_student("Jill")
    await engine.students.add_student("Will")
    await engine.students.add_student("Bill")

    async with engine.students.get_queryable() as students:
        async for student in students.where(lambda s: s.first_name.startswith("J")):
            print(student.first_name)

            # John
            # Johnny
            # Jill

        # Prev filter is applied yet
        all_are_j = await students.all_async(lambda s: s.first_name.startswith("J"))
        print(all_are_j)
        # True


if __name__ == "__main__":
    asyncio.run(main())
