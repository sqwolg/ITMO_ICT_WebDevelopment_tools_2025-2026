from fastapi import HTTPException
from models import Todo
from schemas import TodoModel, TodoCreateModel, TodoUpdateModel, UserModel


class TodoService():
    @staticmethod
    async def get_todos_from_user(user: UserModel) -> list[TodoModel]:
        return [dict(todo) | {"owner_id": user.id} for todo in user.todos]

    @staticmethod
    async def get(todo_id: int, get_query: bool = False) -> Todo:
        todo = Todo.filter(id=todo_id)
        if not get_query:
            todo = await todo.first()
        todo_exists_query = await todo.exists() if get_query else True
        if not todo or not todo_exists_query:
            raise HTTPException(
                status_code=404,
                detail=f"Todo with id {todo_id} not found"
            )
        return todo

    @staticmethod
    async def create(todo_data: TodoCreateModel, user: UserModel) -> Todo:
        todo_dict = todo_data.dict()
        todo_dict.update({"owner_id": user.id})
        return await Todo.create(**todo_dict)

    @staticmethod
    async def update(todo_id: int, todo_data: TodoUpdateModel, user: UserModel) -> Todo:
        todo = await TodoService.get(todo_id)
        todo_query = await TodoService.get(todo_id, get_query=True)
        if todo.owner_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can not edit this todo"
            )
        await todo_query.update(**todo_data.dict(exclude_unset=True))
        return await todo_query.first()

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
