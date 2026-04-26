import fastapi

from todo_app.services import tags as tags_service
from todo_app.services import users as users_service
from todo_app.schemas import tags as tags_schema
from todo_app.schemas import users as users_schema

router = fastapi.APIRouter(prefix="/tags")


@router.post(
    path="/",
    response_model=tags_schema.TagResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def create_tag(
    create_request: tags_schema.CreateTagRequest,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    )
):
    return await tags_service.TagService.create(
        create_request,
        owner_id=current_user.id,
    )


@router.get(
    path="/my",
    response_model=list[tags_schema.TagResponse],
)
async def get_tags_for_current_user(
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    )
):
    tags = [
        tags_schema.TagResponse(
            id=tag.id,
            title=tag.title,
            owner_id=current_user.id,
            todos=[
                tags_schema.Todo.model_validate(todo, from_attributes=True)
                for todo in tag.todos
            ],
        )
        for tag in current_user.tags
    ]
    return tags


@router.get(
    path="/{tag_id}",
    response_model=tags_schema.TagResponse,
)
async def get_tag(
    tag_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    )
):
    return await tags_service.TagService.get(
        tag_id=tag_id,
        owner_id=current_user.id,
    )


@router.put(
    path="/{tag_id}",
    response_model=tags_schema.TagResponse,
)
async def update_tag(
    tag_id: int,
    update_request: tags_schema.UpdateTagRequest,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    )
):
    return await tags_service.TagService.update(
        update_request=update_request,
        tag_id=tag_id,
        owner_id=current_user.id,
    )


@router.delete(
    path="/{tag_id}",
    response_model=tags_schema.TagResponse,
)
async def update_tag(
    tag_id: int,
    current_user: users_schema.UserModel = fastapi.Depends(
        users_service.UserService.get_current_user,
    )
):
    return await tags_service.TagService.delete(
        tag_id=tag_id,
        owner_id=current_user.id,
    )
