import celery
import requests

from todo_app import settings
from todo_app.schemas import parser as parser_schemas

celery_app = celery.Celery(
    __name__,
    broker=settings.settings.redis_url,
    backend=settings.settings.redis_url,
)

@celery_app.task
def parse_url(parse_request: str) -> str:
    try:
        response = requests.post(url=settings.settings.parser_url, data=parse_request)
        response.raise_for_status()
        json = response.json()
    except Exception as err:
        return str(err)

    return json.get("result", "error")
