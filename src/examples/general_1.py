# pylint: skip-file

import asyncio
from datetime import datetime

from sjd import TEntity, Engine, properties as props, make_property, PropertyOptions


@props.auto_collect()
class Order(TEntity):

    # A reference to order's owner ( a Customer instance )
    customer_id = props.reference()

    # Description will be automatically collected from __init__ parameters.
    def __init__(self, description: str) -> None:
        self.description = description
        self._created_at_iso_fmt = datetime.now().isoformat()  # private field

    # Here our private property _created_at_iso_fmt will be covered by created_at
    # property, which is a python property as well as sjd property
    @make_property(
        str,
        options=PropertyOptions(init=False, required=True),
        binder="_created_at_iso_fmt",  # Get or set from this, but save in created_at
    )
    def created_at(self):
        # _created_at_iso_fmt is an str field which stores an iso format of datetime
        return datetime.fromisoformat(self._created_at_iso_fmt)


@props.auto_collect()
class Customer(TEntity):

    # A virtual list of orders, saved in a separate collection Order.
    orders = props.from_entities(Order, "customer_id")

    def __init__(self, username: str, *orders: Order) -> None:
        self.username = username
        if orders:
            self.orders = list(orders)


class AppEngine(Engine):
    __db_path__ = "__test_db__"
    customers = Engine.set(Customer)

    # A custom method to create orders
    async def create_order(self, customer_username: str, order_description: str):
        customer = await self.customers.get_first_async("username", customer_username)
        if customer:
            # Iter over virtually saved orders
            async for order in self.customers.iter_referenced_by_async(
                customer, lambda c: c.orders
            ):
                if order.description == order_description:
                    return False

            customer.orders.append(Order(order_description))
        else:
            customer = Customer(customer_username, Order(order_description))
            self.customers.add(customer)
        await self.customers.save_changes_async()
        return True


async def main():

    engine = AppEngine()

    await engine.create_order("immmdreza", "Gimme some faith ...")
    await engine.create_order("immmdreza", "Gimme some hope ...")


if __name__ == "__main__":
    asyncio.run(main())
