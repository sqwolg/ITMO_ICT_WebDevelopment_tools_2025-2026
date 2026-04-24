## Задание

Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

Подробности задания:

1. Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async.
2. Каждая программа должна содержать функцию parse_and_save(url), которая будет загружать HTML-страницу по указанному URL, парсить ее, сохранять заголовок страницы в базу данных и выводить результат на экран.
3. Используйте базу данных из лабораторной работы номер 1 для заполенния ее данными. Если Вы не понимаете, какие таблицы и откуда Вы могли бы заполнить с помощью парсинга, напишите преподавателю в общем чате потока.
4. Для threading используйте модуль threading, для multiprocessing - модуль multiprocessing, а для async - ключевые слова async/await и модуль aiohttp для асинхронных запросов.
5. Создайте список нескольких URL-адресов веб-страниц для парсинга и разделите его на равные части для параллельного парсинга.
6. Запустите параллельный парсинг для каждой программы и сохраните данные в базу данных.
7. Замерьте время выполнения каждой программы и сравните результаты.

## Решение

### Подключение к базе данных

```python
import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = os.getenv("DB_URL")
DATABASE_URL_ASYNC = os.getenv("DB_ASYNC_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean)


def init_db():
    Base.metadata.create_all(bind=engine)


async def async_init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

```

### Threading

```python
import threading
import requests
import time
from database import SessionLocal, Todo, init_db

URLS = [f"https://dummyjson.com/todos?skip={i}&limit=25" for i in range(0, 251, 25)]


def parse_and_save(url):
    response = requests.get(url)
    todos = response.json()["todos"]
    
    session = SessionLocal()
    for todo in todos:
        t = Todo(id=todo["id"], title=todo["todo"], completed=todo["completed"])
        session.merge(t)
    session.commit()
    session.close()
    print(f"Thread saved {len(todos)} items from {url}")


def run():
    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    init_db()
    start = time.time()
    run()
    print(f"Threading completed in {time.time() - start:.2f}s")
```

Результат:

```
Thread saved 4 items from https://dummyjson.com/todos?skip=250&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=100&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=25&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=50&limit=25 
Thread saved 25 items from https://dummyjson.com/todos?skip=225&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=150&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=75&limit=25 
Thread saved 25 items from https://dummyjson.com/todos?skip=175&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=0&limit=25  
Thread saved 25 items from https://dummyjson.com/todos?skip=125&limit=25
Thread saved 25 items from https://dummyjson.com/todos?skip=200&limit=25
Threading completed in 1.15s
```

Особенности:

- Использует threading.Thread
- Каждый поток загружает данные и сохраняет в БД
- SQLAlchemy ORM используется синхронно

### Multiprocessing

```python
import multiprocessing
import requests
import time
from database import SessionLocal, Todo, init_db

URLS = [f"https://dummyjson.com/todos?skip={i}&limit=25" for i in range(0, 251, 25)]


def parse_and_save(url):
    response = requests.get(url)
    todos = response.json()["todos"]

    session = SessionLocal()
    for todo in todos:
        t = Todo(id=todo["id"], title=todo["todo"], completed=todo["completed"])
        session.merge(t)
    session.commit()
    session.close()
    print(f"Process saved {len(todos)} items from {url}")


def run():
    with multiprocessing.Pool(processes=4) as pool:
        pool.map(parse_and_save, URLS)


if __name__ == "__main__":
    init_db()
    start = time.time()
    run()
    print(f"Multiprocessing completed in {time.time() - start:.2f}s")
```

Результат:

```
Process saved 25 items from https://dummyjson.com/todos?skip=0&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=50&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=25&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=75&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=100&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=125&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=150&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=175&limit=25
Process saved 4 items from https://dummyjson.com/todos?skip=250&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=225&limit=25
Process saved 25 items from https://dummyjson.com/todos?skip=200&limit=25
Multiprocessing completed in 2.43s
```

Особенности:

Использует multiprocessing.Pool
- Каждый процесс выполняет парсинг и сохранение отдельно
- SQLAlchemy ORM вызывается отдельно в каждом процессе
- PostgreSQL корректно работает с многопроцессными запросами

### Asyncio

```python
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
```

Результат:

```
Saved 4 items from https://dummyjson.com/todos?skip=250&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=100&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=50&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=125&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=175&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=25&limit=25 
Saved 25 items from https://dummyjson.com/todos?skip=75&limit=25 
Saved 25 items from https://dummyjson.com/todos?skip=0&limit=25  
Saved 25 items from https://dummyjson.com/todos?skip=200&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=150&limit=25
Saved 25 items from https://dummyjson.com/todos?skip=225&limit=25
Asyncio completed in 0.76s
```

Особенности:

- Использует aiohttp для загрузки
- Использует SQLAlchemy 2.0 с asyncpg
- Каждый запрос обрабатывается асинхронно
- Данные сохраняются в PostgreSQL с использованием AsyncSession

### Результаты

|      Подход     | Результат (с) |
| :-------------: | :-----------: |
| Threading       | 1.15          |
| Multiprocessing | 2.43          |
| Asyncio         | 0.76          |

Выводы:

- Asyncio оказался наиболее эффективным для сетевых операций, благодаря неблокирующему I/O.
- Threading чуть медленнее из-за накладных расходов, связанных с потоками.
- Multiprocessing показал худший результат из-за еще больших накладных расходов при работе с процессами.
