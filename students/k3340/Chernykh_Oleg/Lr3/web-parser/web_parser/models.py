import pydantic


class ParseUrlRequest(pydantic.BaseModel):
    url: pydantic.HttpUrl


class ParseUrlResponse(pydantic.BaseModel):
    url: pydantic.HttpUrl
    result: str
