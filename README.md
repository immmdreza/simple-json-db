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
from sjd.database import Engine, __Collection__

class AppEngine(Engine):

    students = __Collection__(Student)

    def __init__(self):
        super().__init__(Path("__test_db__"))

```

1. The engine will create a directory named `__test_db__`.
2. inside `__test_db__` the collections are stored.
3. You **SHOULD** pass the type of your entity (`entity_type`) to the `__Collection__`. Here is `Student`.
4. type `__Collection__` is a descriptor! The actual thing is `Collection`.
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

### Complex Properties

You can use more complex models! models that include Other models as property or a list of other models or builtin types.

Let's begin with creating another model called `Grade` that includes some information about an student's grade in a course. We are going to add this to `Student` later.

Since this model is an embed entity, You should inherit from `EmbedEntity`.

```py
from src.entity import TEntity, EmbedEntity

# ---- sniff ----

class Grade(EmbedEntity):
    __json_init__ = True

    course_id = IntProperty(required=True)
    course_name = StrProperty(required=True)
    score = IntProperty(required=True)

    def __init__(self, course_id: int, course_name: str, score: int):
        self.course_id = course_id
        self.course_name = course_name
        self.score = score
```

To add this as a new property to the `Student`, we'll use `ComplexProperty`. ( Or `OptionalComplexProperty` for a complex property which is not required ).

Your `Student` class should looks like this:

```py
from src.entity.properties import IntProperty, StrProperty, OptionalComplexProperty

# ---- sniff ----

class Student(TEntity):
    __json_init__ = True

    student_id = IntProperty(required=True)
    first_name = StrProperty(required=True)
    last_name = StrProperty()
    grade = OptionalComplexProperty(Grade)

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
jill = await collection.as_queryable.first(lambda s: s.first_name == "Jill")
    if jill.grade:
        print(jill.grade.course_name, jill.grade.score)

# Math
```

### List Properties

As we all know, there may be more than one course per student! Then the grade property, can be grades.

```py
from src.entity.properties import IntProperty, StrProperty, ListProperty

# ---- sniff ----

class Student(TEntity):
    __json_init__ = True

    student_id = IntProperty(required=True)
    first_name = StrProperty(required=True)
    last_name = StrProperty()
    grades = ListProperty(Grade, default_factory=list)

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
jill = await collection.as_queryable.first(lambda s: s.first_name == "Jill")
if jill.grades:
    jill.grades[-1].score = 50
    await collection.update(jill)
```

Oh who's score was 50 ??!

```py
with_50_score = await collection.as_queryable.where(
    lambda s: any(x.score == 50 for x in s.grades)).single()
print(with_50_score.first_name)
```

_That's all for now, check `Collection` object for more ..._
