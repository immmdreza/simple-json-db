# simple-json-db

This is a simple json database.
The package provides a simple ORM between python objects and
json objects with a well type-hinted schema.

This package maps your python objects to json and then you can save, get,
modify or delete them using async methods.

_This package is for tiny and simple projects. with a low amount of data._

## Installation

The package is available at [PYPI](https://pypi.org/project/json-entity) as json-entity.

## Intro

Let's see how you can get started with the package.

See also our [Wiki](https://github.com/immmdreza/simple-json-db/wiki).

You can take a look at [src/examples](src/examples), if you're not on reading mode.

## Quick Start

This data base consist of 3 main elements:

1- **Model**

    It's obvious that you should have a model for your data to save, update, or ...
    
    Since this library works with json, your model can contain everything
    that JSON can.

2- **Collection**

    You have a collection of data for every model, therefor,
    The relation between Model and Collection is one to one.

3- **Engine**

    This is where all collections are operate.

So, Every `Engine` has some `Collection`s where each collection
contains a set of an unique `Model`.

### Let's create a model

Models are simple python class.

```py
from sjd import TEntity, Engine, properties as props

@props.auto_collect()
class Person(TEntity):
    def __init__(self, first_name: int, last_name: str, age: int):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
```

Using `auto_collect()` method,
the model will automatically collect properties form `__init__` method.

### Creating collection ?

It's really not necessary to create a collection by your own! And maybe you better )

Let us do that for ya ( Of course you can create customized Collections ).

### Setup engine

Now you need to setup database's engine and define your collections there.

```py
# ---- sniff ----

class AppEngine(Engine):

    persons = Engine.set(Person)

    def __init__(self):
        super().__init__("MoyDatabase")
```

That's all you need to do for now.

### Fire up

Now it's time for some fireworks 🎇.

_Since the package is `async`, you'll need an event loop for it._

```py
import asyncio

# ---- sniff ----

async def main():
    ...


if __name__ == "__main__":
    asyncio.run(main())
```

Now you can work with database inside main function.

```py
async def main():

    engine = AppEngine()
    collection = engine.persons

    collection.add_range(
        Person("John", "Doe", 20),
        Person("Jane", "Doe", 21),
        Person("Jack", "jones", 22),
        Person("Jill", "jones", 23),
    )
    await collection.save_changes_async()

```

Iterate over all persons in the collection

```py
async for person in collection:
    print(person.first_name, person.last_name, person.age)
```

You can do more advanced query stuff with `queryable context`.

```py
async with collection.get_queryable() as persons:
    async for person in persons.where(lambda p: p.age > 21):
        print(person.first_name, person.last_name, person.age)
```

Or get only one directly.

```py
target = await collection.get_first_async(lambda s: s.first_name, "John")
```

You can easily update your data:

```py
async with collection.get_queryable() as persons:
    async for person in persons.where(lambda p: p.last_name == "jones"):
        person.last_name = "Jones"

await collection.save_changes_async()
```

Or even delete them ...

```py
async with collection.get_queryable() as persons:
    async for person in persons.where(lambda p: p.last_name == "Doe"):
        collection.delete(person)

await collection.save_changes_async()
```

There're a lot more! see [src/examples](src/examples).
