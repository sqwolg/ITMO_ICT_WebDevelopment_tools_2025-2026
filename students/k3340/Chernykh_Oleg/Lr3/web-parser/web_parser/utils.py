import asyncio
from collections.abc import AsyncGenerator

import aiohttp
import bs4
import fastapi


async def get_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


async def get_url_heading(url: str, session: aiohttp.ClientSession) -> str:
    # sleep to simulate long operation
    await asyncio.sleep(15)

    async with session.get(url) as response:
        if response.status != fastapi.status.HTTP_200_OK:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request to {url} failed with status {response.status}",
            )
        
        html = await response.text()
        soup = bs4.BeautifulSoup(html, "lxml")
        title = soup.find("title")

        if not title:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=f"No title found at page {url}",
            )

        return title.text.strip()
