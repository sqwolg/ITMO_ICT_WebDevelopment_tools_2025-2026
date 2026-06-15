from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=32, unique=True)
    password = fields.CharField(max_length=256)
    created_at = fields.DatetimeField(auto_now_add=True)
    todos: fields.ReverseRelation["Todo"]
    tags: fields.ReverseRelation["Tag"]
    todo_lists: fields.ReverseRelation["TodoList"]
    edits: fields.ReverseRelation["EditLog"]

    class PydanticMeta:
        exclude = ("password",)


class TodoTag(Model):
    id = fields.IntField(pk=True)
    todo = fields.ForeignKeyField("models.Todo")
    tag = fields.ForeignKeyField("models.Tag")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = (("todo", "tag"),)


class Todo(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=128, null=True)
    is_completed = fields.BooleanField(default=False)
    updated_at = fields.DatetimeField(auto_now=True)
    owner: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", realted_name="todos", to_field="id", null=True
    )
    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="todos", through="models.TodoTag",
    )
    todo_list: fields.ForeignKeyRelation["TodoList"] = fields.ForeignKeyField(
        "models.TodoList", realted_name="todos", to_field="id", null=True
    )
    edits: fields.ReverseRelation["EditLog"]


class Tag(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    owner: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", realted_name="todos", to_field="id"
    )
    todos: fields.ManyToManyRelation[Todo]


class TodoList(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    owner: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", realted_name="todo_lists", to_field="id"
    )
    todos: fields.ReverseRelation["Todo"]


class EditLog(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", realted_name="edits", to_field="id"
    )
    todo: fields.ForeignKeyRelation[Todo] = fields.ForeignKeyField(
        "models.Todo", realted_name="edits", to_field="id"
    )
    new_value = fields.CharField(max_length=1000)
    updated_at = fields.DatetimeField(auto_now_add=True)
