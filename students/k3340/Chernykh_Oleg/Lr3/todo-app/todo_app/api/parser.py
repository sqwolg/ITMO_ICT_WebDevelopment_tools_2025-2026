from collections.abc import AsyncGenerator
from typing import Annotated

import aiohttp
import celery
import celery.result
import fastapi

from todo_app import settings, tasks
from todo_app.schemas import parser as parser_schemas
from todo_app.schemas import UserModel, TodoCreateModel
from todo_app.services import TodoService, UserService

router = fastapi.APIRouter(prefix="/parser")


async def get_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


@router.post("/parse", response_model=parser_schemas.ParseUrlResponse)
async def parse(
    parse_request: parser_schemas.ParseUrlRequest,
    session: Annotated[aiohttp.ClientSession, fastapi.Depends(get_session)],
    user: UserModel = fastapi.Depends(UserService.get_current_user)
):
    try:
        async with session.post(
            url=settings.settings.parser_url,
            json=parse_request.model_dump(),
        ) as response:
            response.raise_for_status()
            json = await response.json()
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    response = parser_schemas.ParseUrlResponse.model_validate(json)
    await TodoService.create(
        TodoCreateModel(title=response.result, description=str(response.url)),
        user,
    )
    return response


@router.post("/parse/start", response_model=parser_schemas.ParserTaskResponse)
async def strart_parsing(
    parse_request: parser_schemas.ParseUrlRequest,
    user: UserModel = fastapi.Depends(UserService.get_current_user),
):
    task = tasks.parse_url.delay(parse_request.model_dump_json())
    return parser_schemas.ParserTaskResponse(id=task.id, state="STARTED")


@router.get("/parse/result/{task_id}", response_model=parser_schemas.ParserTaskResponse)
async def get_parsing_result(
    task_id: str,
    user: UserModel = fastapi.Depends(UserService.get_current_user),
):
    result = celery.result.AsyncResult(task_id)

    if result.state == "FAILURE":
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(result.result),
        )
    
    if result.state == "SUCCESS":
        await TodoService.create(
            TodoCreateModel(title=result.result),
            user,
        )
        return parser_schemas.ParserTaskResponse(
            id=task_id,
            state=result.state,
            result=result.result,
        )

    return parser_schemas.ParserTaskResponse(
        id=task_id,
        state=result.state,
    )
