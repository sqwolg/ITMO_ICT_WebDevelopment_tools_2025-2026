import fastapi
import tortoise
import tortoise.queryset

from todo_app import models
from todo_app.schemas import todo_list as todo_list_schema


class TodoListService:
    @staticmethod
    async def create(
        create_request: todo_list_schema.CreateTodoListRequest,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        todo_list_dict = create_request.model_dump()
        todo_list_dict.update({"owner_id": user_id})
        todo_list_model = await models.TodoList.create(**todo_list_dict)

        response = todo_list_schema.TodoListResponse(
            id=todo_list_model.id,
            title=todo_list_model.title,
            description=todo_list_model.description,
            created_at=todo_list_model.created_at,
        )

        return response

    @staticmethod
    def _get_query_by_id(todo_list_id: int) -> tortoise.queryset.QuerySet[models.TodoList]:
        return models.TodoList.filter(id=todo_list_id)

    @staticmethod
    async def _check_existence(todo_list_id: int) -> None:
        query = TodoListService._get_query_by_id(todo_list_id)
        todo_list_exists = await query.exists()

        if not todo_list_exists:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Todo list with id {todo_list_id} not found",
            )
    
    @staticmethod
    async def _check_owner(
        todo_list_id: int,
        user_id: int,
    ) -> models.TodoList:
        query = TodoListService._get_query_by_id(todo_list_id)
        todo_list_model = await query.prefetch_related("todos").first()

        if todo_list_model.owner_id != user_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=f"Todo list with id {todo_list_id} was created by another user",
            )

        return todo_list_model
    
    @staticmethod
    async def add_todo(
        todo_list_id: int,
        todo_id: int,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        await TodoListService._check_existence(todo_list_id)
        todo_list_model = await TodoListService._check_owner(todo_list_id, user_id)
        todo_model = await models.Todo.filter(id=todo_id).first()

        if not todo_model:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )

        if todo_model.owner_id != user_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=f"Todo with id {todo_id} was create by another user",
            )

        await models.Todo.filter(id=todo_id).update(todo_list_id=todo_list_id)
        await todo_list_model.fetch_related("todos")

        return todo_list_schema.TodoListResponse.model_validate(
            todo_list_model,
            from_attributes=True,
        )

    @staticmethod
    async def get(
        todo_list_id: int,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        await TodoListService._check_existence(todo_list_id)
        todo_list_model = await TodoListService._check_owner(todo_list_id, user_id)
        return todo_list_schema.TodoListResponse.model_validate(
            todo_list_model,
            from_attributes=True,
        )

    @staticmethod
    async def update(
        update_request: todo_list_schema.UpdateTodoListRequest,
        todo_list_id: int,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        await TodoListService._check_existence(todo_list_id)
        todo_list_model = await TodoListService._check_owner(todo_list_id, user_id)

        todo_list_query = TodoListService._get_query_by_id(todo_list_id)
        await todo_list_query.update(**update_request.model_dump(exclude_unset=True))

        return todo_list_schema.TodoListResponse.model_validate(
            todo_list_model,
            from_attributes=True,
        )

    @staticmethod
    async def delete(
        todo_list_id: int,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        await TodoListService._check_existence(todo_list_id)
        todo_list_model = await TodoListService._check_owner(todo_list_id, user_id)

        todo_list_query = TodoListService._get_query_by_id(todo_list_id)
        await todo_list_query.delete()

        return todo_list_schema.TodoListResponse.model_validate(
            todo_list_model,
            from_attributes=True,
        )

    @staticmethod
    async def delete_todo(
        todo_list_id: int,
        todo_id: int,
        user_id: int,
    ) -> todo_list_schema.TodoListResponse:
        await TodoListService._check_existence(todo_list_id)
        todo_list_model = await TodoListService._check_owner(todo_list_id, user_id)
        todo_model = await models.Todo.filter(id=todo_id).first()

        if not todo_model:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )

        if todo_model.owner_id != user_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=f"Todo with id {todo_id} was create by another user",
            )

        await models.Todo.filter(id=todo_id).update(todo_list_id=None)
        await todo_list_model.fetch_related("todos")

        return todo_list_schema.TodoListResponse.model_validate(
            todo_list_model,
            from_attributes=True,
        )
