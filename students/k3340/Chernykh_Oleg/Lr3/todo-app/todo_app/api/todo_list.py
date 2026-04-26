import fastapi
from todo_app.schemas import todo_list as todo_list_schema
from todo_app.schemas import users as users_schema
from todo_app.services import users as users_service
from todo_app.services import todo_list as todo_list_service

router = fastapi.APIRouter(prefix="/todo_lists")


@router.post("/", response_model=todo_list_schema.TodoListResponse)
async def create_todo_list(
    create_request: todo_list_schema.CreateTodoListRequest,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.create(
        create_request=create_request,
        user_id=current_user.id,
    )


@router.post("/{todo_list_id}/todo/{todo_id}", response_model=todo_list_schema.TodoListResponse)
async def add_todo(
    todo_list_id: int,
    todo_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.add_todo(
        todo_list_id=todo_list_id,
        todo_id=todo_id,
        user_id=current_user.id,
    )


@router.get("/my", response_model=list[todo_list_schema.TodoListResponse])
async def get_todo_lists(
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> list[todo_list_schema.TodoListResponse]:
    todo_lists = [
        todo_list_schema.TodoListResponse.model_validate(
            todo_list,
            from_attributes=True,
        )
        for todo_list in current_user.todolists
    ]

    return todo_lists


@router.get("/{todo_list_id}", response_model=todo_list_schema.TodoListResponse)
async def get_todo_list(
    todo_list_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.get(
        todo_list_id=todo_list_id,
        user_id=current_user.id,
    )


@router.put("/{todo_list_id}", response_model=todo_list_schema.TodoListResponse)
async def update_todo_list(
    todo_list_id: int,
    update_request: todo_list_schema.UpdateTodoListRequest,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.update(
        update_request=update_request,
        todo_list_id=todo_list_id,
        user_id=current_user.id,
    )


@router.delete("/{todo_list_id}", response_model=todo_list_schema.TodoListResponse)
async def delete_todo_list(
    todo_list_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.delete(
        todo_list_id=todo_list_id,
        user_id=current_user.id,
    )


@router.delete("/{todo_list_id}/todo/{todo_id}", response_model=todo_list_schema.TodoListResponse)
async def delete_todo(
    todo_list_id: int,
    todo_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    ),
) -> todo_list_schema.TodoListResponse:
    return await todo_list_service.TodoListService.delete_todo(
        todo_list_id=todo_list_id,
        todo_id=todo_id,
        user_id=current_user.id,
    )
