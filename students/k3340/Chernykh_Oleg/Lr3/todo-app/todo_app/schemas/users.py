from typing import Optional
from pydantic import BaseModel, constr
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import Tortoise
from todo_app.models import User


class UserBaseModel(BaseModel):
    username: constr(max_length=32)
    password: constr(max_length=256, min_length=8)

    class Config:
        extra = "forbid"


class UserCreateModel(UserBaseModel):
    pass


class UserUpdateModel(BaseModel):
    username: Optional[constr(max_length=32, min_length=1)]
    password: Optional[constr(max_length=256, min_length=8)]

    class Config:
        extra = "forbid"


class UpdateUserPassword(BaseModel):
    old_password: constr(max_length=256, min_length=8)
    new_password: constr(max_length=256, min_length=8)


Tortoise.init_models(["todo_app.models"], "models")
UserModel = pydantic_model_creator(
    User,
    name="UserModel",
    include=(
        "id",
        "username",
        "created_at",
        "todos",
        "tags",
        "todo_lists",
        "edits",
    )
)
