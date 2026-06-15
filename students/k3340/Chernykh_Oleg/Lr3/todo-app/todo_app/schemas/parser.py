from typing import Annotated

import pydantic


class ParseUrlRequest(pydantic.BaseModel):
    url: Annotated[pydantic.HttpUrl, pydantic.AfterValidator(str)]


class ParseUrlResponse(pydantic.BaseModel):
    url: pydantic.HttpUrl
    result: str


class ParserTaskResponse(pydantic.BaseModel):
    id: str
    state: str
    result: str | None = None
