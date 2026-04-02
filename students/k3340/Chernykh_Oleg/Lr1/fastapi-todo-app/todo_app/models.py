from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=32, unique=True)
    password = fields.CharField(max_length=256)
    created_at = fields.DatetimeField(auto_now_add=True)

    class PydanticMeta:
        exclude = ("password",)


class Todo(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=128, null=True)
    is_completed = fields.BooleanField(default=False)
    updated_at = fields.DatetimeField(auto_now=True)
    owner = fields.ForeignKeyField(
        "models.User", realted_name="todos", to_field="id", null=True)
