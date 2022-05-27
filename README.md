# simple-json-db

This is a simple json database. The package provides a simple ORM between python objects and json objects with a well type-hinted schema.

This package maps your python objects to json and then you can save, get, modify or delete them using async methods.

_This package is for tiny and simple projects. with a low amount of data._

## Installation

The package is available at [PYPI](https://pypi.org/project/json-entity) as json-entity.

## Intro

Let's see how you can get started with the package.

See also our [Wiki](https://github.com/immmdreza/simple-json-db/wiki).

You can take a look at [src/examples](src/examples), if you're not on reading mode.

### Create Model

Step #1 is to create a model that represents something like a row in a table.

```py
from sjd import TEntity, properties as props

class Student(TEntity):
    student_id = props.IntProperty(required=True)
    first_name = props.StrProperty(required=True)
    last_name = props.StrProperty(required=True)
```

1. Your model should inherit from `TEntity`.
2. Properties can be anything that JSON supports (`int`, `str` for now).

### Initialize db

We have an `Engine` and some `Collection`s. The first one is your database, the second is your table.

```py
from sjd import Engine

class AppEngine(Engine):

    students = Engine.set(Student)

    def __init__(self):
        super().__init__(Path("__test_db__"))

```

1. The engine will create a directory named `__test_db__`.
2. inside `__test_db__` the collections are stored.
3. You **SHOULD** pass the type of your entity (`entity_type`) to the `__Collection__`. Here is `Student`.
4. `Engine.set()` returns type `__Collection__` which is a descriptor! The actual thing is `Collection`.
5. The collection name will be class variable's name ( `students` here ).

### Create engine instance

After setting up engine, you can create an instance of it. And you have access to the collections.

```py
engine = AppEngine()

collection = engine.students
```

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

    student_id = props.IntProperty(required=True)
    first_name = props.StrProperty(required=True)
    last_name = props.StrProperty()

    def __init__(self, student_id: int, first_name: str, last_name: str):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
```

1. For models with `__init__` that accepts some parameters, you **SHOULD** include `__json_init__ = True` or it will fail while deserializing the data.

<details>
    <summary>Even Quicker</summary>

    Package provides a way to resolve model's properties from `__init__` function, without specifing them directly.
    
    This can be used for simple models only.
    
    ```py
    from src.sjd import TEntity, properties as props

    @props.collect_props_from_init
    class Student(TEntity):
        def __init__(self, student_id: int, first_name: str, last_name: str):
            self.student_id = student_id
            self.first_name = first_name
            self.last_name = last_name

    ```
</details>

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
async for student in engine.students.iterate_by(
    lambda s: s.last_name, "Doe"
):
    print(student.first_name)

# John
# Jane
# Jack
# Jill
```

Ops they were all "Doe".

```py
async for student in engine.students.iterate_by(
    lambda s: s.first_name, "John"
):
    print(student.first_name)

# John
```

If it's going to be one, we have more options.

```py

student = await collection.get_first(lambda s: s.first_name == "John")
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

### Complex Properties

You can use more complex models! models that include Other models as property or a list of other models or builtin types.

Let's begin with creating another model called `Grade` that includes some information about an student's grade in a course. We are going to add this to `Student` later.

Since this model is an embed entity, You should inherit from `EmbedEntity`.

```py
from sjd import TEntity, EmbedEntity, properties as props

# ---- sniff ----

class Grade(EmbedEntity):
    __json_init__ = True

    course_id = props.IntProperty(required=True)
    course_name = props.StrProperty(required=True)
    score = props.IntProperty(required=True)

    def __init__(self, course_id: int, course_name: str, score: int):
        self.course_id = course_id
        self.course_name = course_name
        self.score = score
```

To add this as a new property to the `Student`, we'll use `ComplexProperty`. ( Or `OptionalComplexProperty` for a complex property which is not required ).

Your `Student` class should looks like this:

```py

# ---- sniff ----

class Student(TEntity):
    __json_init__ = True

    student_id = props.IntProperty(required=True)
    first_name = props.StrProperty(required=True)
    last_name = props.StrProperty()
    grade = props.OptionalComplexProperty(Grade)

    def __init__(
        self,
        student_id: int,
        first_name: str,
        last_name: str,
        grade: Optional[Grade] = None,
    ):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.grade = grade
```

1. Note that we passed `Grade` type as the first parameter to the `OptionalComplexProperty`.

Now we can add this grade for all students

```py
async for student in collection:
    student.grade = Grade(1, "Math", 90)
    await collection.update(student)
```

Let's check if it's working

```py
jill = await collection.get_first(lambda s: s.first_name == "Jill")
    if jill.grade:
        print(jill.grade.course_name, jill.grade.score)

# Math
```

### List Properties

As we all know, there may be more than one course per student! Then the grade property, can be grades.

```py

# ---- sniff ----

class Student(TEntity):
    __json_init__ = True

    student_id = props.IntProperty(required=True)
    first_name = props.StrProperty(required=True)
    last_name = props.StrProperty()
    grades = props.ListProperty(Grade, default_factory=list)

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
```

Let's update all of entities again.

```py
async for student in collection:
    student.grades = [Grade(1, "Math", 90), Grade(2, "English", 80)]
    await collection.update(student)

# Math 90
# English 80
```

Let's change Jill's english score to 50.

```py
jill = await collection.get_first(lambda s: s.first_name == "Jill")
if jill.grades:
    jill.grades[-1].score = 50
    await collection.update(jill)
```

Oh who's score was 50 ??!

```py
async with collection.iterate() as students:

    with_50_score = await students.where(
        lambda s: any(x.score == 50 for x in s.grades)).single()
    print(with_50_score.first_name)
```

### Getting data ( Fast way )

There are two methods that are probably faster than `as_queryable` way.

1. `get(__id: str)`

    Get an entity by it's id, Which is (`entity.id`). We use this for `update` and `delete` method.

2. `iterate_by(__prop: str, __value: Any)`

    Use this to do an `async iterate` over all entities with `entity[__prop] == __value`.
    We use this to work with virtual objects.

3. `get_first(__prop: str, __value: Any)`

    Just like 2, but returns the first.

```py
async for student in engine.students.iterate_by("first_name", "Jill"):
    print(student.last_name)
```

or

```py
async for student in engine.students.iter_by_prop_value(lambda s: s.first_name, "Jill"):
    print(student.last_name)
```

### Virtual properties

It was a good idea to use another model inside our main model to store additional data, but we don't actually want to load all of data while getting our main model. ( You don't want to load students's grade every time, since it's costly. )

It's better use a separate entity for grade and make it related to the student. Here, the grade will be a `virtual complex property`.

And the grade will use a `reference property` to the student id.

Since the `Grade` is going to be a separate entity, we should add it to our `AppEngine`.

1. First, let's modify the `Student` class.

    We will replace `ListProperty` with `VirtualListProperty`.

    ```py
    # ---- sniff ----

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

    ```

    `VirtualListProperty` takes type of entity it refers to and the name of `ReferenceProperty` which we'll declare later inside `Grade` class ( `student_id` ).

2. Modifying `Grade`.

    The class should inherit from `TEntity` instead of `EmbedEntity`, since it's a separate entity now.

    ```py
    # ---- sniff ----

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
    ```

    Note that we added `student_id = ReferenceProperty()`. The attribute name should be the same we declared inside `Student`'s `VirtualListProperty`'s second parameter (`student_id`).

3. Finally, modifying `AppEngine`

    We only need to add `Grade` to the `AppEngine`, just like `Student`.

    ```py
    class AppEngine(Engine):

        students = Engine.set(Student)
        grades = Engine.set(Grade)

        def __init__(self):
            super().__init__("__test_db__")
    ```

4. **Add data**. You can now add your data just like before.

    ```py
    engine = AppEngine()

    await engine.students.add(
        Student(1, "Arash", "Doe", [Grade(1, "Physics", 20)]),
    )
    ```

5. Getting data

    If you try getting one of your students now, you'll see the `grades` property is an empty list.

    ```py
    arash = await engine.students.get_first(
        lambda s: s.first_name == "Arash"
    )
    print(arash.grades)

    # []
    ```

    _The `grades` is some kind of `lazy property`._

    to load virtual data, you can use method `load_virtual_props`

    ```py
    await engine.students.load_virtual_props(arash)
    print(arash.grades)

    # [<__main__.Grade object at 0x0000021B3AF7FAC0>]
    ```

    or you can specify property's name ( if you have more than one ).

    ```py
    await engine.students.load_virtual_props(arash, "grades")
    print(arash.grades)
    ```

    Here you go, you have your grades.

    **Or even better**, you can iter over grades WITHOUT calling `load_virtual_props` ( less costly again ).

    You use `iter_referenced_by`:

    ```py
    async for grade in engine.students.iter_referenced_by(arash, lambda s: s.grades):
        print(grade.course_name)
    ```

_Working examples are available under [src/examples](src/examples)._
