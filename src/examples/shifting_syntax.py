import asyncio

from sjd import TEntity, Engine, properties as props


@props.auto_collect()
class Customer(TEntity):
    def __init__(self, name: str) -> None:
        self.name = name


class AppEngine(Engine):
    __db_path__ = "__test_db__"
    customers = Engine.set(Customer)


async def main():

    engine = AppEngine()
    customers_collection = engine.customers

    async with customers_collection:  # <-- this will save changes automatically on exit
        customers_collection <<= Customer("Arash"), Customer("Sara")
        tracked = Customer("Kiarash") >> customers_collection
        # Both of above ways will call add() method of customers_collection
        # using second way, you can only add one! but you receive a free tracking instance
        # which contains information about changes in entity, and entity id.
        print("A new entity will be added with id:", tracked.key)

    async with customers_collection:
        async for customer in customers_collection:
            customers_collection >>= customer
            # Using above syntax is same as calling: customers_collection.delete(customer)
            break

        # Again, using below syntax, you can get tracking instance as well.
        async for customer in customers_collection:
            tracked = customer << customers_collection
            print(f"An entity with id {tracked.key}, is going to be deleted!")

    # NOTE: no other kind of shifting are allowed only these four!
    # ---------------------------------------------
    # To add:
    #   one - Entity >> Collection of Entities
    #   two - Collection of Entities <<= Entity, Entities
    # ---------------------------------------------
    # To delete:
    #   three - Entity << Collection of Entities
    #   four  - Collection of Entities >>= Entity, Entities

    # You see? Only four!


if __name__ == "__main__":
    asyncio.run(main())
