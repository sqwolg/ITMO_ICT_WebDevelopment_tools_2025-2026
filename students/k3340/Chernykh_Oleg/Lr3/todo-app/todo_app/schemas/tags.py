import datetime

import pydantic


class Todo(pydantic.BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool
    updated_at: datetime.datetime


class BaseTag(pydantic.BaseModel):
    title: pydantic.constr(strip_whitespace=True, max_length=20)


class TagResponse(BaseTag):
    id: int
    owner_id: int
    todos: list[Todo] = pydantic.Field(default_factory=list)


class CreateTagRequest(BaseTag):
    pass


class UpdateTagRequest(BaseTag):
    pass
