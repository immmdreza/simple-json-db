import asyncio
from typing import Optional

from sjd import TEntity, Engine, properties as props


# Create a model to store.
class Student(TEntity):
    __json_init__ = True  # This is required if you wanna use __init__.

    # Here are some properties to store.
    first_name = props.StrProperty(required=True)
    last_name = props.OptionalProperty(str)

    def __init__(self, first_name: str, last_name: Optional[str]):
        self.first_name = first_name
        self.last_name = last_name


# Setup the engine
class AppEngine(Engine):

    # Add a collection which is for model Student
    students = Engine.register_collection(Student)

    def __init__(self):
        super().__init__("__test_db__")


engine = AppEngine()


async def main():

    students = engine.students

    await students.add(Student("John", "Doe"))

    john = await students.get_first(lambda s: s.first_name, "John")
    if john:
        print(john.id)


if __name__ == "__main__":
    asyncio.run(main())
