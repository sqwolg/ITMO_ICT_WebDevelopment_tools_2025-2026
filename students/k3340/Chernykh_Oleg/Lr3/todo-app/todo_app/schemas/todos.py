from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr, Field


class Tag(BaseModel):
    id: int
    title: str


class TodoBaseModel(BaseModel):
    title: constr(max_length=64, min_length=1)
    description: constr(max_length=128) | None = None


class TodoCreateModel(TodoBaseModel):
    tags: list[int] = Field(default_factory=list)


class TodoUpdateModel(BaseModel):
    title: Optional[constr(max_length=64, min_length=1)]
    description: Optional[constr(max_length=128)]
    is_completed: Optional[bool]
    tags: list[int] | None = None


class TodoModel(TodoBaseModel):
    id: int
    owner_id: int
    is_completed: bool
    updated_at: datetime
    tags: list[Tag]
    todo_list_id: int | None = None


class EditLog(BaseModel):
    id: int
    user_id: int
    todo_id: int
    new_value: str
    updated_at: datetime
