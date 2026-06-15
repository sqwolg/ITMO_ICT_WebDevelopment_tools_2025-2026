from fastapi import APIRouter, Depends, HTTPException
from todo_app.schemas import EditLog, TodoModel, TodoCreateModel, TodoUpdateModel, UserModel
from todo_app.services import TodoService, UserService
from todo_app.services.tags import TagService


router = APIRouter(prefix="/todos")


@router.get("/edits", response_model=list[EditLog])
async def get_edit_logs(user: UserModel = Depends(UserService.get_current_user)):
    schemas = []
    for edit in user.editlogs:
        schemas.append(
            EditLog(
                id=edit.id,
                user_id=user.id,
                todo_id=edit.todo.id,
                updated_at=edit.updated_at,
                new_value=edit.new_value,
            ),
        )
    return schemas


@router.get("/edits/{edit_id}", response_model=EditLog)
async def get_edit_logs(
    edit_id: int,
    user: UserModel = Depends(UserService.get_current_user),
):
    for edit in user.editlogs:
        if edit.id == edit_id:
            return EditLog(
                id=edit.id,
                user_id=user.id,
                todo_id=edit.todo.id,
                updated_at=edit.updated_at,
                new_value=edit.new_value,
            )

    raise HTTPException(status_code=404, detail=f"Edit with id {edit_id} not found")


@router.get("/my", response_model=list[TodoModel])
async def get_todos(user: UserModel = Depends(UserService.get_current_user)):
    return await TodoService.get_todos_from_user(user)


@router.post("/", response_model=TodoModel)
async def create_todo(
    data: TodoCreateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    todo_model = await TodoService.create(data, user)

    tag_models = []
    for tag_id in data.tags:
        _, tag_model = await TagService.get_query_and_model(tag_id, user.id)
        tag_models.append(tag_model)

    for tag_model in tag_models:
        await todo_model.tags.add(tag_model)

    await todo_model.fetch_related("tags")

    return todo_model

@router.put("/{todo_id}", response_model=TodoModel)
async def update_todo(
    todo_id: int,
    data: TodoUpdateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    tag_models = []
    for tag_id in data.tags:
        _, tag_model = await TagService.get_query_and_model(tag_id, user.id)
        tag_models.append(tag_model)

    todo_model = await TodoService.update(todo_id, data, user)
        
    await todo_model.tags.clear()

    for tag_model in tag_models:
        await todo_model.tags.add(tag_model)

    await todo_model.fetch_related("tags")

    return todo_model



@router.delete("/{todo_id}", response_model=TodoModel)
async def delete_todo(
    todo_id: int,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await TodoService.delete(todo_id, user)
