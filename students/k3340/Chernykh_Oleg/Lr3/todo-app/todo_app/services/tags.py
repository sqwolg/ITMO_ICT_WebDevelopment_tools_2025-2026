import fastapi
import tortoise
import tortoise.queryset

from todo_app import models
from todo_app.schemas import tags


class TagService:
    @staticmethod
    async def create(create_request: tags.CreateTagRequest, owner_id: int) -> tags.TagResponse:
        tag_dict = create_request.model_dump()
        tag_dict.update({"owner_id": owner_id})
        tag_model = await models.Tag.create(**tag_dict)

        response = tags.TagResponse(
            id=tag_model.id,
            owner_id=owner_id,
            title=tag_model.title,
        )

        return response

    @staticmethod
    async def get_query_and_model(
        tag_id: int,
        owner_id: int,
    ) -> tuple[tortoise.queryset.QuerySet[models.Tag], models.Tag]:
        tag_query = models.Tag.filter(id=tag_id)
        tag_exists = await tag_query.exists()

        if not tag_exists:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Tag with id {tag_id} not found"
            )
            
        tag = await tag_query.prefetch_related("todos").first()

        if tag.owner_id != owner_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=f"Tag with id {tag_id} was created by another user",
            )

        return tag_query, tag

    @staticmethod
    async def get(tag_id: int, owner_id: int) -> tags.TagResponse:
        _, tag_model = await TagService.get_query_and_model(tag_id, owner_id)
        response = tags.TagResponse.model_validate(tag_model, from_attributes=True)
        return response

    @staticmethod
    async def update(
        update_request: tags.UpdateTagRequest,
        tag_id: int,
        owner_id: int,
    ) -> tags.TagResponse:
        tag_query, tag_model = await TagService.get_query_and_model(tag_id, owner_id)
        await tag_query.update(**update_request.model_dump(exclude_unset=True))

        response = tags.TagResponse(
            id=tag_id,
            title=update_request.title,
            owner_id=owner_id,
            todos=[tags.Todo.model_validate(todo, from_attributes=True) for todo in tag_model.todos],
        )
        return response

    @staticmethod
    async def delete(tag_id: int, owner_id: int) -> tags.TagResponse:
        tag_query, tag_model = await TagService.get_query_and_model(tag_id, owner_id)
        await tag_query.delete()

        response = tags.TagResponse(
            id=tag_id,
            title=tag_model.title,
            owner_id=owner_id,
            todos=[tags.Todo.model_validate(todo, from_attributes=True) for todo in tag_model.todos],
        )
        return response
