from typing import Optional
from pydantic import BaseModel, constr
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise import Tortoise
from models import User


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


Tortoise.init_models(["models"], "models")
UserModel = pydantic_model_creator(User)
