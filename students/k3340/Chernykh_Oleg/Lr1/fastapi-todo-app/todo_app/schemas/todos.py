from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr


class TodoBaseModel(BaseModel):
    title: constr(max_length=64, min_length=1)
    description: constr(max_length=128) = None

    class Config:
        extra = "forbid"


class TodoCreateModel(TodoBaseModel):
    pass


class TodoUpdateModel(BaseModel):
    title: Optional[constr(max_length=64, min_length=1)]
    description: Optional[constr(max_length=128)]
    is_completed: Optional[bool]

    class Config:
        extra = "forbid"


class TodoModel(TodoBaseModel):
    id: int
    owner_id: int
    is_completed: bool
    updated_at: datetime

    class Config:
        orm_mode = True
