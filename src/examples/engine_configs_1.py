import asyncio
from typing import Optional

from sjd import Engine, TEntity, properties as props


class _Days(TEntity):
    employee_id = props.reference()

    def __init__(self, days: int) -> None:
        self.days = days


@props.auto_collect()
class RestInfo(_Days):
    pass


@props.auto_collect()
class StandbyInfo(_Days):
    pass


@props.auto_collect()  # This won't override attributes you've already defined ( rest_info & standby_info here ).
class Employee(TEntity):

    rest_info = props.from_entity(RestInfo, "employee_id")
    standby_info = props.from_entity(StandbyInfo, "employee_id")

    def __init__(
        self,
        employee_id: int,
        first_name: str,
        last_name: str,
        rest_info: Optional[RestInfo] = None,
        standby_info: Optional[StandbyInfo] = None,
    ) -> None:
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.rest_info = rest_info
        self.standby_info = standby_info


class AppEngine(Engine):

    employees = Engine.set(Employee)
    # No need to add rest_info & standby_info collections here. but you can.
    # rest_info = Engine.set(RestInfo)
    # standby_info = Engine.set(StandbyInfo)

    def __init__(self):
        super().__init__("__test_db__")

        # Say welcome to lambda hell ...
        self._configs.config_collection(
            lambda engine: engine.employees,
            lambda collection: collection.config_property(
                lambda employee: employee.rest_info,
                lambda config: config.delete_whole_reference(),
            ).config_property(
                lambda employee: employee.standby_info,
                lambda config: config.delete_reference_prop(),
            ),
        ),


async def main():
    engine = AppEngine()
    employees_col = engine.employees

    await employees_col.add(Employee(1, "John", "Doe", RestInfo(5), StandbyInfo(5)))

    async for item in employees_col:
        await employees_col.delete(item)
    # Due to engine configs, this'll delete the rest_info entity too.
    # But the standby_info entity will not be deleted entirely only StandbyInfo.employee_id will be None.


if __name__ == "__main__":
    asyncio.run(main())
