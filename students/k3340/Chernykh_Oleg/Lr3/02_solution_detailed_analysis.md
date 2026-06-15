# Подробный разбор решения

## 1. Базовое объяснение

В решении лабораторной работа разбита на два приложения:

- `todo-app` - основное FastAPI-приложение с пользователями, todo, авторизацией, базой данных и API для вызова парсера.
- `web-parser` - отдельное FastAPI-приложение, которое принимает URL, загружает страницу и достает из HTML тег `<title>`.

Также используются инфраструктурные сервисы:

- `postgres` - база данных PostgreSQL;
- `redis` - брокер очереди и backend результатов Celery;
- `celery_worker` - отдельный worker, который выполняет задачи парсинга в фоне.

Все сервисы описаны в `docker-compose.yaml`.

## 2. Как устроен Docker Compose

Файл `docker-compose.yaml` поднимает пять сервисов.

### `postgres`

PostgreSQL запускается из образа `postgres:15-alpine`.

Важные настройки:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` задают пользователя, пароль и базу;
- `postgres_data` сохраняет данные между перезапусками;
- `healthcheck` через `pg_isready` позволяет дождаться готовности базы;
- сервис подключен к сети `app-network`.

### `todo_app`

Это основной backend.

Он собирается из папки `./todo-app` по `Dockerfile`.

Важные переменные окружения:

- `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` - подключение к PostgreSQL;
- `PARSER_HOST=web_parser`, `PARSER_PORT=8000` - адрес сервиса парсера внутри Docker-сети;
- `REDIS_HOST=redis`, `REDIS_PORT=6379`, `REDIS_PASSWORD=redispass` - адрес Redis.

Порт `8000` проброшен наружу:

```yaml
ports:
  - "8000:8000"
```

Поэтому с хоста можно открыть:

```text
http://localhost:8000/docs
```

### `web_parser`

Это отдельный FastAPI-сервис парсера.

Он собирается из папки `./web-parser` и не публикует порт наружу через `ports`. Вместо этого используется:

```yaml
expose:
  - 8000
```

Это значит, что сервис доступен другим контейнерам внутри Docker-сети, но не обязательно доступен напрямую с хоста.

Основное приложение обращается к нему по имени сервиса:

```text
http://web_parser:8000/parse
```

### `redis`

Redis запускается из образа `redis:7-alpine`.

Он используется Celery как:

- broker - очередь задач;
- backend - место хранения результатов.

Redis запущен с паролем:

```yaml
command: redis-server --requirepass ${REDIS_PASSWORD:-redispass}
```

### `celery_worker`

Worker собирается из той же папки `todo-app`, но использует отдельный Dockerfile:

```text
Dockerfile.celery_worker
```

Команда запуска:

```text
poetry run celery -A todo_app.tasks worker --loglevel=info
```

Это значит: Celery должен найти приложение и задачи в модуле `todo_app.tasks`.

## 3. Dockerfile основного приложения

`todo-app/Dockerfile`:

1. Берет базовый образ `python:3.13-slim`.
2. Устанавливает `curl`.
3. Устанавливает Poetry.
4. Копирует проект в `/app`.
5. Запускает `poetry install`.
6. Открывает порт `8000`.
7. Запускает `entrypoint.sh`.

`entrypoint.sh` сначала применяет миграции:

```sh
poetry run aerich upgrade
```

Потом запускает приложение:

```sh
exec poetry run todo_app
```

Это важный момент: контейнер сам приводит базу к актуальной схеме перед стартом API.

## 4. Dockerfile парсера

`web-parser/Dockerfile` устроен похожим образом:

1. Базовый образ `python:3.13-slim`.
2. Установка Poetry.
3. Копирование исходников.
4. Установка зависимостей.
5. Открытие порта `8000`.
6. Запуск команды:

```text
poetry run parser
```

Команда `parser` объявлена в `web-parser/pyproject.toml`:

```toml
[tool.poetry.scripts]
parser = "web_parser.main:main"
```

## 5. Основной FastAPI backend

В `todo_app/main.py` создается FastAPI-приложение:

```python
app = FastAPI()
app.include_router(router)
```

Затем регистрируется Tortoise ORM:

```python
register_tortoise(
    app,
    db_url=settings.database_url,
    modules={"models": ["todo_app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
```

Это связывает приложение с PostgreSQL.

Все API-маршруты собираются в `todo_app/api/__init__.py`:

- `/parser` - маршруты лабораторной 3;
- `/todos` - todo;
- `/users` - пользователи и авторизация;
- `/tags` - теги;
- `/todo_list` - списки todo.

## 6. Сервис парсера

Парсер находится в `web-parser/web_parser/main.py`.

Главный endpoint:

```text
POST /parse
```

Он принимает модель:

```python
class ParseUrlRequest(pydantic.BaseModel):
    url: pydantic.HttpUrl
```

Затем вызывает:

```python
result = await utils.get_url_heading(url=str(parse_request.url), session=session)
```

В `utils.get_url_heading` происходит основная логика:

1. Искусственная задержка `await asyncio.sleep(15)`.
2. HTTP GET к переданному URL через `aiohttp`.
3. Проверка статуса ответа.
4. Чтение HTML.
5. Разбор HTML через BeautifulSoup.
6. Поиск тега `<title>`.
7. Возврат текста заголовка страницы.

Задержка на 15 секунд нужна не для реального парсинга, а для демонстрации долгой операции. Благодаря ей хорошо видно отличие синхронного вызова от асинхронного через очередь.

## 7. Синхронный вызов парсера

Синхронный endpoint находится в `todo_app/api/parser.py`:

```text
POST /parser/parse
```

Что он делает:

1. Принимает JSON с URL.
2. Проверяет текущего пользователя через `UserService.get_current_user`.
3. Создает `aiohttp.ClientSession`.
4. Отправляет POST-запрос в parser-service.
5. Ждет ответ от парсера.
6. Валидирует ответ через Pydantic.
7. Создает todo с результатом парсинга.
8. Возвращает клиенту результат.

Ключевой фрагмент:

```python
async with session.post(
    url=settings.settings.parser_url,
    json=parse_request.model_dump(),
) as response:
    response.raise_for_status()
    json = await response.json()
```

Здесь используется `settings.settings.parser_url`. Он собирается из переменных окружения:

```python
return f"http://{self.parser_host}:{self.parser_port}/parse"
```

В Docker Compose указано:

```yaml
PARSER_HOST: "web_parser"
PARSER_PORT: 8000
```

Поэтому внутри контейнера получается адрес:

```text
http://web_parser:8000/parse
```

После успешного парсинга результат сохраняется как todo:

```python
await TodoService.create(
    TodoCreateModel(title=response.result, description=str(response.url)),
    user,
)
```

То есть если страница имеет title `Example Domain`, в todo создается задача с таким заголовком.

## 8. Асинхронный вызов через Celery

Асинхронный сценарий состоит из трех частей:

- endpoint для постановки задачи;
- Celery task;
- endpoint для получения результата.

### Постановка задачи

Endpoint:

```text
POST /parser/parse/start
```

Код:

```python
task = tasks.parse_url.delay(parse_request.model_dump_json())
return ParserTaskResponse(id=task.id, state="STARTED")
```

Метод `delay()` не выполняет функцию сразу внутри FastAPI. Он отправляет задачу в Redis. FastAPI быстро получает `task.id` и возвращает его клиенту.

### Celery task

Файл `todo_app/tasks.py`:

```python
celery_app = celery.Celery(
    __name__,
    broker=settings.settings.redis_url,
    backend=settings.settings.redis_url,
)
```

Redis URL строится так:

```python
redis://:redispass@redis:6379/0
```

Сама задача:

```python
@celery_app.task
def parse_url(parse_request: str) -> str:
    response = requests.post(url=settings.settings.parser_url, data=parse_request)
    response.raise_for_status()
    json = response.json()
    return json.get("result", "error")
```

Worker забирает задачу из Redis, отправляет запрос в parser-service и возвращает строку с результатом.

### Получение результата

Endpoint:

```text
GET /parser/parse/result/{task_id}
```

Он создает объект:

```python
result = celery.result.AsyncResult(task_id)
```

Дальше проверяет состояние:

- если `FAILURE`, возвращает HTTP 500;
- если `SUCCESS`, создает todo и возвращает результат;
- если задача еще не готова, возвращает текущее состояние.

При `SUCCESS` результат тоже сохраняется в todo:

```python
await TodoService.create(
    TodoCreateModel(title=result.result),
    user,
)
```

## 9. Что особенно важно по условию

### Парсер вызывается по HTTP

Условие требует реализовать возможность вызова парсера по HTTP. В решении это сделано отдельным FastAPI-приложением `web-parser` с endpoint `/parse`.

Это хороший вариант, потому что парсер становится самостоятельным сервисом.

### Основной FastAPI вызывает парсер из другого контейнера

В синхронном endpoint основной backend обращается к parser-service по внутреннему имени Docker Compose:

```text
web_parser
```

Это демонстрирует понимание Docker-сетей: контейнеры внутри одной сети видят друг друга по именам сервисов.

### Есть Dockerfile для FastAPI и парсера

В решении есть:

- `todo-app/Dockerfile`;
- `web-parser/Dockerfile`;
- `todo-app/Dockerfile.celery_worker`.

Отдельный Dockerfile для worker не обязателен теоретически, но это понятное и удобное решение, потому что worker запускается другой командой.

### Есть Docker Compose

Compose описывает все необходимые сервисы:

- приложение;
- парсер;
- PostgreSQL;
- Redis;
- worker.

Это закрывает требование по оркестрации контейнеров.

### Есть вызов через очередь

Это закрывает третью подзадачу на полный балл:

- Redis добавлен;
- Celery добавлен;
- worker добавлен;
- task определен;
- endpoint постановки задачи есть;
- endpoint проверки результата есть.

## 10. Сложные моменты

### Почему в синхронном варианте используется `aiohttp`

Основной FastAPI endpoint объявлен как `async def`. Внутри него лучше использовать асинхронный HTTP-клиент, чтобы не блокировать event loop.

Поэтому используется:

```python
aiohttp.ClientSession
```

Если бы внутри `async def` использовался обычный `requests`, то поток выполнения блокировался бы до завершения сетевого запроса.

### Почему в Celery task используется `requests`

Celery task объявлен как обычная синхронная функция:

```python
def parse_url(...)
```

Внутри worker это нормально: задача выполняется не в event loop FastAPI, а в отдельном процессе worker. Поэтому можно использовать обычный `requests`.

### Почему нужен Redis

Celery сам по себе не хранит очередь. Ему нужен брокер сообщений.

В этой работе Redis выполняет сразу две роли:

- принимает задачи от FastAPI;
- хранит результаты, чтобы потом можно было получить их по `task_id`.

### Почему клиенту возвращается `task_id`

Асинхронная операция не может сразу вернуть результат, потому что worker еще не выполнил задачу. Поэтому API возвращает идентификатор задачи.

Клиент должен:

1. Запустить задачу.
2. Сохранить `task_id`.
3. Через некоторое время спросить результат.

### Почему результат сохраняется в todo

Это показывает интеграцию лабораторной 3 с приложением из лабораторной 1. Парсер не просто возвращает строку, а создает полезную сущность в базе данных.

В синхронном варианте сохраняются:

- title как `title`;
- исходный URL как `description`.

В асинхронном варианте сохраняется title как `title`.

### Почему нужна авторизация

Маршруты парсера требуют текущего пользователя:

```python
user: UserModel = Depends(UserService.get_current_user)
```

Это нужно, чтобы созданный todo был привязан к конкретному пользователю.

На сдаче важно показать не только `/parser/parse`, но и то, что сначала нужно:

1. Создать пользователя.
2. Получить токен.
3. Выполнять запросы с `Authorization: Bearer <token>`.

## 11. Замечания по качеству решения

Решение в целом закрывает все пункты условия и тянет на полный вариант, потому что реализованы Docker, Compose, отдельный parser-service, Redis и Celery worker.

Есть несколько мест, которые полезно понимать перед сдачей.

### Опечатка в переменной `POSTGERS_DB`

В `docker-compose.yaml` у `todo_app` написано:

```yaml
DATABASE_NAME: ${POSTGERS_DB:-todos}
```

Вероятно, имелось в виду `POSTGRES_DB`. Сейчас это не критично, потому что есть значение по умолчанию `todos`. Но если задавать переменную окружения `POSTGRES_DB`, основной backend ее не подхватит из-за опечатки.

На защите можно сказать: "Да, тут есть опечатка в имени env-переменной, но дефолт совпадает с базой. В production я бы поправил на `POSTGRES_DB`".

### Отправка JSON в Celery task через `data`

В `tasks.py` используется:

```python
requests.post(url=settings.settings.parser_url, data=parse_request)
```

Надежнее было бы отправлять JSON так:

```python
requests.post(url=settings.settings.parser_url, json=json.loads(parse_request))
```

или хотя бы добавить заголовок `Content-Type: application/json`.

Синхронный вариант сделан более корректно, потому что там используется параметр `json=...`.

### При каждом чтении успешного результата может создаваться новый todo

Endpoint `GET /parser/parse/result/{task_id}` при состоянии `SUCCESS` создает todo. Если вызвать этот endpoint несколько раз с тем же `task_id`, можно получить несколько одинаковых todo.

Для учебной лабораторной это допустимо, но в реальном проекте лучше было бы:

- сохранять связь `task_id -> todo_id`;
- проверять, был ли результат уже обработан;
- не создавать дубликаты.

### Обработка ошибок в Celery task

Сейчас при исключении task возвращает строку ошибки:

```python
except Exception as err:
    return str(err)
```

Из-за этого Celery может считать задачу успешной, хотя фактически парсинг завершился ошибкой. Для более строгой логики лучше пробрасывать исключение дальше, чтобы состояние стало `FAILURE`.

## 12. Итоговая оценка соответствия условию

Решение соответствует основным требованиям:

- FastAPI приложение упаковано в Docker.
- Парсер упакован в Docker.
- PostgreSQL поднят через Docker Compose.
- Парсер вызывается по HTTP.
- Основное FastAPI-приложение имеет endpoint для вызова парсера.
- Redis добавлен.
- Celery worker добавлен.
- Есть endpoint для постановки задачи в очередь.
- Есть endpoint для получения результата.

Главная демонстрационная идея: синхронный endpoint ждет около 15 секунд, а асинхронный endpoint сразу возвращает `task_id`, потому что работа уходит в Celery worker.

