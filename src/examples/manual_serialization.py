# pylint: skip-file

from sjd import properties as props
from sjd.serialization import serialize, deserialize


class MySubModel:
    sub_id = props.IntProperty()


class MyModel:
    model_id = props.IntProperty()
    sub_model = props.ComplexProperty(MySubModel)


my_sub = MySubModel()
my_sub.sub_id = 123456

my_model = MyModel()
my_model.model_id = 1234567
my_model.sub_model = my_sub


print(serialize(my_model))
# {'model_id': 1234567, 'sub_model': {'sub_id': 123456}}

deserialized = deserialize(MyModel, serialize(my_model))
if deserialized:
    print(deserialized.model_id)
    # 1234567


my_sub_2 = MySubModel()
my_sub_2.sub_id = 9876431

print(serialize([my_sub, my_sub_2]))
# [{'sub_id': 123456}, {'sub_id': 9876431}]


deserialized_list = deserialize(MySubModel, [{"sub_id": 123456}, {"sub_id": 9876431}])
if deserialized_list:
    print(deserialized_list)
    # [<__main__.MySubModel object at 0x00000253B1029F60>,
    # <__main__.MySubModel object at 0x00000253B1029F90>]
