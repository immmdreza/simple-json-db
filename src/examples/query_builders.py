# pylint: skip-file

import asyncio
import datetime
from typing import Optional

from sjd import TEntity, Engine, properties as props


@props.auto_collect()
class Student(TEntity):
    def __init__(
        self,
        first_name: str,
        registered_date: datetime.datetime,
        last_name: Optional[str] = None,
    ):
        self.first_name = first_name
        self.registered_date = registered_date
        self.last_name = last_name


class AppEngine(Engine):
    __db_path__ = "__test_db__"
    students = Engine.set(Student)


async def main():

    engine = AppEngine()
    students_col = engine.students

    students_col.add_range(
        Student("Johnny", datetime.datetime(2001, 7, 20), "Deep"),
        Student("Jececa", datetime.datetime(2000, 6, 10), "Doe"),
        Student("Jack", datetime.datetime(2001, 6, 5), "Makron"),
    )

    await engine.save_changes_async()

    target_date = datetime.datetime(2001, 1, 1)
    async for new_student in students_col.find_all_async(
        students_col.qa.gt(lambda s: s.registered_date, target_date)
    ):
        print(new_student.first_name, new_student.last_name)
        # Johnny Deep
        # Jack Makron


if __name__ == "__main__":
    asyncio.run(main())
