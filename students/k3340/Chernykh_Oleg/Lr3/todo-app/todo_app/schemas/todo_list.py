import datetime

import pydantic

from todo_app.schemas import tags


class BaseTodoList(pydantic.BaseModel):
    title: pydantic.constr(max_length=64, min_length=1)
    description: pydantic.constr(max_length=128) | None = None


class CreateTodoListRequest(BaseTodoList):
    pass


class UpdateTodoListRequest(BaseTodoList):
    title: pydantic.constr(max_length=64, min_length=1) | None = None
    description: pydantic.constr(max_length=128) | None = None


class TodoListResponse(BaseTodoList):
    id: int
    created_at: datetime.datetime
    todos: list[tags.Todo] = pydantic.Field(default_factory=list)
