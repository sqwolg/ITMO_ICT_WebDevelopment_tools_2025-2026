from fastapi import APIRouter
from todo_app.api import parser, tags, todos, todo_list, users


router = APIRouter()
router.include_router(parser.router, tags=["parser"])
router.include_router(todos.router, tags=["todo"])
router.include_router(users.router, tags=["user"])
router.include_router(tags.router, tags=["tags"])
router.include_router(todo_list.router, tags=["todo_list"])
