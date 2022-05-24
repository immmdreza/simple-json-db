# simple-json-db

This is a simple json database. The package provides a simple ORM between python objects and json objects with a well type-hinted schema.

This package maps your python objects to json and then you can save, get, modify or delete them using async methods.

_This package is for tiny and simple projects. with a low amount of data._

## Intro

Let's see how you can get started with the package.

### Create Model

Step #1 is to create a model that represents something like a row in a table.

```py
from sjd.entity.properties import IntProperty, StrProperty
from sjd.entity import TEntity

class Student(TEntity):
    student_id = IntProperty(required=True)
    first_name = StrProperty(required=True)
    last_name = StrProperty(required=True)
```

1. Your model should inherit from `TEntity`.
2. Properties can be anything that JSON supports (`int`, `str` for now).

### Initialize db

We have an `Engine` and some `Collection`s. The first one is your database, the second is your table.

```py
import asyncio
import pathlib

engine = Engine(pathlib.Path("__test_db__"))
collection = Collection(engine, Student)
```

1. The engine will create a directory named `__test_db__`.
2. inside `__test_db__` the collections are stored.
3. You **SHOULD** pass `engine` to the `Collection`.
4. You **SHOULD** pass the type of your entity (`entity_type`) to the `Collection`. Here is `Student`.
5. The collection name will be `entity_type.__name__`.

### Construct first data

Let's create our first data.

```py
student = Student()
student.student_id = 123456789
student.first_name = "Arash"
student.last_name = "Enzo"
```

### Add data

Save data.

```py
await collection.add(student)
```

Good job, you've saved your first data.

### Better model

Personally, i prefer classes with initializers. so let's add an `__init__` to the `Student`.

```py
# ---- sniff ----

class Student(TEntity):
    __json_init__ = True

    student_id = IntProperty(required=True)
    first_name = StrProperty(required=True)
    last_name = StrProperty()

    def __init__(self, student_id: int, first_name: str, last_name: str):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
```

1. For models with `__init__` that accepts some parameters, you **SHOULD** include `__json_init__ = True` or it will fail while deserializing the data.

### Add more data

Now we can create more students quickly, so we need to add them quickly as well.

```py
await collection.add_many(
    Student(1, "John", "Doe"),
    Student(2, "Jane", "Doe"),
    Student(3, "Jack", "Doe"),
    Student(4, "Jill", "Doe"),
)
```

### Query data

Let's do some query stuff to get data we want.

Iterate over all.

```py
async for student in collection:
    print(student.first_name)

# John
# Jane
# Jack
# Jill
```

Get data with some filters.

```py
async for student in collection.as_queryable.where(
    lambda s: s.last_name == "Doe"
):
    print(student.first_name)

# John
# Jane
# Jack
# Jill
```

Ops they were all "Doe".

```py
async for student in collection.as_queryable.where(
    lambda s: s.first_name == "John"
):
    print(student.first_name)

# John
```

If it's going to be one, we have more options.

```py

student = await collection.as_queryable.first(lambda s: s.first_name == "John")
print(student.first_name)

# John
```

And some more ...

_Type hint are fully available._

### Update data

I guess the name was Johnny not John 🤔, let's change the name of student John to Johnny.

```py
async for student in collection:
    if student.first_name == "John":
        student.first_name = "Johnny"
        collection.update(student)
```

### Delete data

Now that i looked closer, we don't have any john or johnny at all, imma remove johnny then.

```py
async for student in collection:
    if student.first_name == "Johnny":
        collection.delete(student)
```

_That's all for now, check `Collection` object for more ..._
