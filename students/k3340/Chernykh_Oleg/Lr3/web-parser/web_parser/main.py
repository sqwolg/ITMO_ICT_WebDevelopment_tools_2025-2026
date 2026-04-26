from typing import Annotated

import aiohttp
import fastapi
import uvicorn

from web_parser import models, utils

app = fastapi.FastAPI()


@app.post("/parse", response_model=models.ParseUrlResponse)
async def parse(
    parse_request: models.ParseUrlRequest,
    session: Annotated[aiohttp.ClientSession, fastapi.Depends(utils.get_session)],
):
    try:
        result = await utils.get_url_heading(url=str(parse_request.url), session=session)
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return models.ParseUrlResponse(
        url=parse_request.url,
        result=result,
    )


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
