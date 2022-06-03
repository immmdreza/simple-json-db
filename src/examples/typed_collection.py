# pylint: skip-file


import asyncio

from sjd import Engine, Collection, TEntity, properties as props


@props.auto_collect()
class Employee(TEntity):
    def __init__(self, employee_id: int, first_name: str, last_name: str):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name


class EmployeeCollection(Collection[Employee]):
    def __init__(self, engine: "Engine", /) -> None:
        super().__init__(engine, Employee, "employeesCollection")

    async def add_employee(self, first_name: str, last_name: str) -> None:
        added_count = await self.count_async()
        employee_id = 100000 + added_count
        self.add(Employee(employee_id, first_name, last_name))
        await self.save_changes_async()


class AppEngine(Engine):

    employees = Engine.typed_set(Employee, EmployeeCollection)

    def __init__(self):
        super().__init__("__test_db__")


async def main():
    engine = AppEngine()
    employees_col = engine.employees

    await employees_col.add_employee("John", "Smite")
    await employees_col.add_employee("Tommy", "Smite")
    await employees_col.add_employee("Sara", "Smite")
    await employees_col.add_employee("Andy", "Smite")

    async for employee in employees_col:
        print(employee.employee_id)

    # 100000
    # 100001
    # 100002
    # 100003


if __name__ == "__main__":
    asyncio.run(main())
