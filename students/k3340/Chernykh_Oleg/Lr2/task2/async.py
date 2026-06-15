import asyncio
import aiohttp
import time
from database import AsyncSessionLocal, Todo, async_init_db

URLS = [f"https://dummyjson.com/todos?skip={i}&limit=25" for i in range(0, 251, 25)]


async def parse_and_save(session_http, url):
    async with session_http.get(url) as response:
        data = await response.json()
        todos = data.get("todos", [])
        
        async with AsyncSessionLocal() as db_session:
            for todo in todos:
                t = Todo(id=todo["id"], title=todo["todo"], completed=todo["completed"])
                await db_session.merge(t)
            await db_session.commit()
        
        print(f"Saved {len(todos)} items from {url}")


async def main():
    await async_init_db()
    async with aiohttp.ClientSession() as session_http:
        tasks = [parse_and_save(session_http, url) for url in URLS]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Asyncio completed in {time.time() - start:.2f}s")
