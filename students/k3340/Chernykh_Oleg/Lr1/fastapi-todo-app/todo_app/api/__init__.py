from fastapi import APIRouter
from api import todos, users


router = APIRouter()
router.include_router(todos.router)
router.include_router(users.router)
