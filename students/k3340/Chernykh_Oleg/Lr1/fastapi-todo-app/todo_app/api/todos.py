from fastapi import APIRouter, Depends
from schemas import TodoModel, TodoCreateModel, TodoUpdateModel, UserModel
from services import TodoService, UserService


router = APIRouter(prefix="/todos")


@router.get("/my", response_model=list[TodoModel])
async def get_todos(user: UserModel = Depends(UserService.get_current_user)):
    return await TodoService.get_todos_from_user(user)


@router.post("/", response_model=TodoModel)
async def create_todo(
    data: TodoCreateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await TodoService.create(data, user)


@router.put("/{todo_id}", response_model=TodoModel)
async def update_todo(
    todo_id: int,
    data: TodoUpdateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await TodoService.update(todo_id, data, user)


@router.delete("/{todo_id}", response_model=TodoModel)
async def delete_todo(
    todo_id: int,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await TodoService.delete(todo_id, user)
