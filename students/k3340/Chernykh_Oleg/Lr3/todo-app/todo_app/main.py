import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from todo_app.api import router
from todo_app.settings import settings


def main():
    app = FastAPI()
    app.include_router(router)

    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={"models": ["todo_app.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
    )


if __name__ == "__main__":
    main()
