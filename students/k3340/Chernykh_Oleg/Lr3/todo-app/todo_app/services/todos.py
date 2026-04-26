from fastapi import HTTPException
from todo_app.models import EditLog, Todo
from todo_app.schemas import Tag, TodoModel, TodoCreateModel, TodoUpdateModel, UserModel


class TodoService():
    @staticmethod
    async def get_todos_from_user(user: UserModel) -> list[TodoModel]:
        return [
            TodoModel(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                owner_id=user.id,
                is_completed=todo.is_completed,
                tags=[
                    Tag.model_validate(tag, from_attributes=True)
                    for tag in todo.tags
                ],
                updated_at=todo.updated_at,
                todo_list_id=todo.todo_list.id if todo.todo_list else None,
            )
            for todo in user.todos
        ]

    @staticmethod
    async def get(todo_id: int, get_query: bool = False) -> Todo:
        todo = Todo.filter(id=todo_id)
        if not get_query:
            todo = await todo.prefetch_related("tags").first()
        todo_exists_query = await todo.exists() if get_query else True
        if not todo or not todo_exists_query:
            raise HTTPException(
                status_code=404,
                detail=f"Todo with id {todo_id} not found"
            )

        return todo

    @staticmethod
    async def create(todo_data: TodoCreateModel, user: UserModel) -> Todo:
        todo_dict = todo_data.model_dump(exclude={"tags"})
        todo_dict.update({"owner_id": user.id})
        todo_model = await Todo.create(**todo_dict)
        return todo_model

    @staticmethod
    async def update(todo_id: int, todo_data: TodoUpdateModel, user: UserModel) -> Todo:
        todo = await TodoService.get(todo_id)
        todo_query = await TodoService.get(todo_id, get_query=True)
        if todo.owner_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can not edit this todo"
            )
        await todo_query.update(**todo_data.model_dump(exclude_unset=True, exclude={"tags"}))
        todo_model = await todo_query.first()

        await EditLog.create(
            user_id=user.id,
            todo_id=todo_id,
            new_value=todo_data.model_dump_json(exclude_unset=True),
        )

        return todo_model

    @staticmethod
    async def delete(todo_id: int, user: UserModel) -> Todo:
        todo = await TodoService.get(todo_id)
        if todo.owner_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can not delete this todo"
            )
        todo_query = await TodoService.get(todo_id, get_query=True)
        await todo_query.delete()
        return todo
