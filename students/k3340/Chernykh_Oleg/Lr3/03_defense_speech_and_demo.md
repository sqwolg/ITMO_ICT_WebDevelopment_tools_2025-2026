# Текст для сдачи и сценарий демонстрации

## Короткий текст для рассказа

В этой лабораторной я упаковал FastAPI-приложение, базу данных, отдельный сервис парсера, Redis и Celery worker в Docker Compose.

Основное приложение находится в `todo-app`. Это backend для todo с пользователями, авторизацией, PostgreSQL и Tortoise ORM. Парсер вынесен в отдельное приложение `web-parser`. Он принимает URL через endpoint `/parse`, скачивает HTML страницы, достает тег `<title>` через BeautifulSoup и возвращает результат.

В Docker Compose описаны пять сервисов: `postgres`, `todo_app`, `web_parser`, `redis` и `celery_worker`. Все они подключены к одной сети `app-network`, поэтому `todo_app` может обращаться к парсеру по имени сервиса `web_parser`, а Celery worker может обращаться к Redis по имени `redis`.

Я реализовал два способа вызова парсера.

Первый способ - синхронный endpoint `POST /parser/parse`. Клиент отправляет URL в основное приложение, backend делает HTTP-запрос к parser-service, ждет результат, сохраняет title страницы как todo и возвращает результат клиенту.

Второй способ - асинхронный endpoint `POST /parser/parse/start`. Он не ждет завершения парсинга, а ставит задачу в Celery через Redis и сразу возвращает `task_id`. После этого результат можно получить через `GET /parser/parse/result/{task_id}`. Когда задача завершилась, результат также сохраняется в todo.

Чтобы было видно отличие между синхронным и асинхронным подходом, в парсере добавлена искусственная задержка на 15 секунд. Синхронный endpoint все это время ждет ответ, а асинхронный сразу возвращает идентификатор задачи.

## Что показать на сдаче

### 1. Показать структуру проекта

Показать, что в `Lr3` есть:

```text
docker-compose.yaml
todo-app/
web-parser/
```

В `todo-app`:

```text
Dockerfile
Dockerfile.celery_worker
entrypoint.sh
todo_app/api/parser.py
todo_app/tasks.py
todo_app/settings.py
```

В `web-parser`:

```text
Dockerfile
web_parser/main.py
web_parser/utils.py
```

### 2. Показать Docker Compose

Открыть `docker-compose.yaml` и объяснить:

- `postgres` - база данных;
- `todo_app` - основной FastAPI backend, порт `8000:8000`;
- `web_parser` - отдельный сервис парсера;
- `redis` - брокер и backend Celery;
- `celery_worker` - обработчик фоновых задач;
- `depends_on` нужен, чтобы сервисы стартовали в правильном порядке;
- `app-network` дает контейнерам возможность обращаться друг к другу по именам сервисов;
- `postgres_data` и `redis_data` сохраняют данные.

### 3. Запустить проект

Из папки лабораторной:

```bash
cd /Users/sqwolg/Documents/University/3_course/6_sem/Web/repo/ITMO_ICT_WebDevelopment_tools_2025-2026/students/k3340/Chernykh_Oleg/Lr3
docker compose up --build
```

После запуска открыть:

```text
http://localhost:8000/docs
```

### 4. Создать пользователя

В Swagger выполнить:

```text
POST /users/
```

Пример тела:

```json
{
  "username": "oleg",
  "password": "password"
}
```

Если пользователь уже создан, можно перейти сразу к получению токена.

### 5. Получить токен

Выполнить:

```text
POST /users/token
```

В форме указать:

```text
username: oleg
password: password
```

Скопировать `access_token`.

В Swagger нажать `Authorize` и вставить токен.

### 6. Показать синхронный парсинг

Выполнить:

```text
POST /parser/parse
```

Пример тела:

```json
{
  "url": "https://example.com"
}
```

Что сказать:

> Сейчас основной backend отправляет HTTP-запрос в контейнер `web_parser` по адресу `http://web_parser:8000/parse`. Запрос будет ждать около 15 секунд, потому что в парсере специально добавлена задержка для имитации долгой операции.

Ожидаемый ответ:

```json
{
  "url": "https://example.com/",
  "result": "Example Domain"
}
```

После этого показать:

```text
GET /todos/my
```

Там должна появиться todo-запись с title `Example Domain`.

### 7. Показать асинхронный парсинг через очередь

Выполнить:

```text
POST /parser/parse/start
```

Тело:

```json
{
  "url": "https://example.com"
}
```

Ожидаемый ответ:

```json
{
  "id": "какой-то-task-id",
  "state": "STARTED",
  "result": null
}
```

Что сказать:

> Здесь FastAPI не ждет завершения парсера. Он ставит задачу в Redis через Celery и сразу возвращает `task_id`. Дальше задачу выполняет отдельный контейнер `celery_worker`.

### 8. Получить результат фоновой задачи

Скопировать `id` из предыдущего ответа и выполнить:

```text
GET /parser/parse/result/{task_id}
```

Если задача еще выполняется, может вернуться:

```json
{
  "id": "...",
  "state": "PENDING",
  "result": null
}
```

или другое промежуточное состояние.

Через 15 секунд ожидаемый ответ:

```json
{
  "id": "...",
  "state": "SUCCESS",
  "result": "Example Domain"
}
```

После этого снова показать:

```text
GET /todos/my
```

Там появится todo с результатом парсинга.

## Что обязательно проговорить

### Про Docker

> Docker нужен, чтобы приложение запускалось в предсказуемом окружении. Я описал отдельные образы для основного API, парсера и Celery worker. PostgreSQL и Redis запускаются из готовых официальных образов.

### Про Docker Compose

> Docker Compose нужен, потому что приложение состоит из нескольких контейнеров. Он создает общую сеть, поднимает сервисы, задает переменные окружения, volumes и зависимости между контейнерами.

### Про синхронный вызов

> Синхронный вызов проще: клиент ждет, FastAPI ждет, parser-service выполняет работу, результат сразу возвращается. Минус в том, что долгий парсинг блокирует ожидание ответа клиентом.

### Про очередь

> Очередь нужна для долгих задач. FastAPI быстро принимает запрос и кладет задачу в Redis, а Celery worker выполняет ее отдельно. Клиент получает `task_id` и может позже запросить результат.

### Про Redis

> Redis здесь используется как брокер Celery и как backend результатов. То есть через него передаются задачи и в нем хранятся результаты выполнения.

### Про Celery

> Celery worker - отдельный процесс в отдельном контейнере. Он слушает Redis, забирает задачи, вызывает parser-service и возвращает результат.

### Про async

> В синхронном endpoint относительно клиента используется `async` и `aiohttp`, чтобы HTTP-запрос к parser-service не блокировал event loop FastAPI. В Celery task используется `requests`, потому что задача выполняется отдельно от FastAPI в worker-процессе.

## Что можно показать в коде

### Синхронный endpoint

Файл:

```text
todo-app/todo_app/api/parser.py
```

Показать:

```python
@router.post("/parse", response_model=parser_schemas.ParseUrlResponse)
```

И место, где основной backend вызывает parser-service:

```python
session.post(
    url=settings.settings.parser_url,
    json=parse_request.model_dump(),
)
```

### Асинхронный старт задачи

Показать:

```python
task = tasks.parse_url.delay(parse_request.model_dump_json())
```

Объяснить: `delay()` кладет задачу в очередь.

### Получение результата

Показать:

```python
result = celery.result.AsyncResult(task_id)
```

Объяснить: по `task_id` можно узнать состояние и результат задачи.

### Celery task

Файл:

```text
todo-app/todo_app/tasks.py
```

Показать:

```python
celery_app = celery.Celery(
    __name__,
    broker=settings.settings.redis_url,
    backend=settings.settings.redis_url,
)
```

И:

```python
@celery_app.task
def parse_url(parse_request: str) -> str:
```

### Parser-service

Файл:

```text
web-parser/web_parser/utils.py
```

Показать:

```python
soup = bs4.BeautifulSoup(html, "lxml")
title = soup.find("title")
```

Объяснить: парсер извлекает title страницы.

## Мини-план выступления

1. Я поднял приложение как набор контейнеров через Docker Compose.
2. В системе есть основной FastAPI backend, PostgreSQL, отдельный parser-service, Redis и Celery worker.
3. Синхронный endpoint `/parser/parse` напрямую вызывает parser-service и ждет результат.
4. Асинхронный endpoint `/parser/parse/start` ставит задачу в Redis, а Celery worker выполняет ее в фоне.
5. Результат можно получить по `task_id` через `/parser/parse/result/{task_id}`.
6. Результаты парсинга сохраняются как todo, поэтому парсер интегрирован с основной бизнес-логикой приложения.

