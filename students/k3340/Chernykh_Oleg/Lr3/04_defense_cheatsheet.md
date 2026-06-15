# Подсказка для сдачи

## Самое главное в одном абзаце

Лабораторная показывает, как упаковать FastAPI-приложение, PostgreSQL, отдельный сервис парсера, Redis и Celery worker в Docker Compose. Парсер можно вызвать синхронно через `POST /parser/parse`, тогда клиент ждет результат. Также парсер можно вызвать асинхронно через `POST /parser/parse/start`, тогда FastAPI кладет задачу в Redis, Celery worker выполняет ее в фоне, а результат забирается через `GET /parser/parse/result/{task_id}`.

## Основные файлы

```text
docker-compose.yaml
```

Главный файл оркестрации. Описывает `postgres`, `todo_app`, `web_parser`, `redis`, `celery_worker`.

```text
todo-app/Dockerfile
```

Образ основного FastAPI-приложения.

```text
todo-app/Dockerfile.celery_worker
```

Образ Celery worker.

```text
web-parser/Dockerfile
```

Образ сервиса парсера.

```text
todo-app/todo_app/api/parser.py
```

Endpoints для синхронного и асинхронного вызова парсера.

```text
todo-app/todo_app/tasks.py
```

Настройка Celery и задача `parse_url`.

```text
web-parser/web_parser/main.py
web-parser/web_parser/utils.py
```

FastAPI parser-service и логика извлечения `<title>`.

## Команды

Запуск:

```bash
cd /Users/sqwolg/Documents/University/3_course/6_sem/Web/repo/ITMO_ICT_WebDevelopment_tools_2025-2026/students/k3340/Chernykh_Oleg/Lr3
docker compose up --build
```

Swagger:

```text
http://localhost:8000/docs
```

Остановка:

```bash
docker compose down
```

Остановка с удалением volumes:

```bash
docker compose down -v
```

## Endpoints для демонстрации

Создать пользователя:

```text
POST /users/
```

Получить токен:

```text
POST /users/token
```

Посмотреть свои todo:

```text
GET /todos/my
```

Синхронный парсинг:

```text
POST /parser/parse
```

Тело:

```json
{
  "url": "https://example.com"
}
```

Асинхронный старт:

```text
POST /parser/parse/start
```

Тело:

```json
{
  "url": "https://example.com"
}
```

Получить результат:

```text
GET /parser/parse/result/{task_id}
```

## Ожидаемые ответы

Синхронный парсинг:

```json
{
  "url": "https://example.com/",
  "result": "Example Domain"
}
```

Старт фоновой задачи:

```json
{
  "id": "...",
  "state": "STARTED",
  "result": null
}
```

Готовый результат:

```json
{
  "id": "...",
  "state": "SUCCESS",
  "result": "Example Domain"
}
```

## Что сказать, если спросят "зачем Docker?"

Docker фиксирует окружение приложения: Python, зависимости, команду запуска и системные пакеты. Благодаря этому приложение запускается одинаково на разных машинах.

## Что сказать, если спросят "зачем Docker Compose?"

Compose нужен для запуска нескольких контейнеров одной системой. В этой лабораторной нужно одновременно поднять API, parser-service, PostgreSQL, Redis и Celery worker. Compose задает сеть, переменные окружения, volumes и порядок старта.

## Что сказать, если спросят "как контейнеры находят друг друга?"

Они находятся в одной Docker-сети `app-network`. Внутри этой сети можно обращаться к контейнерам по именам сервисов из `docker-compose.yaml`: `web_parser`, `postgres`, `redis`.

## Что сказать, если спросят "почему parser-service отдельно?"

Парсинг - отдельная ответственность. Основной API работает с пользователями и todo, а parser-service занимается только загрузкой страницы и извлечением данных. Такой сервис можно отдельно масштабировать или заменить.

## Что сказать, если спросят "что делает парсер?"

Он принимает URL, делает HTTP GET через `aiohttp`, получает HTML, разбирает его через BeautifulSoup и возвращает текст из тега `<title>`.

## Что сказать, если спросят "почему есть задержка 15 секунд?"

Это имитация долгой операции. Она нужна, чтобы наглядно показать разницу между синхронным вызовом и фоновой обработкой через очередь.

## Что сказать, если спросят "чем синхронный вызов отличается от асинхронного?"

Синхронный `/parser/parse` ждет, пока parser-service закончит работу. Асинхронный `/parser/parse/start` сразу возвращает `task_id`, а сам парсинг выполняет Celery worker в фоне.

## Что сказать, если спросят "что такое Celery?"

Celery - это система фоновых задач. Она позволяет вынести долгую работу из HTTP-запроса в отдельный worker.

## Что сказать, если спросят "что такое Redis в этой работе?"

Redis используется как брокер сообщений и backend результатов для Celery. FastAPI кладет задачу в Redis, worker забирает ее, а результат тоже сохраняется через Redis.

## Что сказать, если спросят "что делает `delay()`?"

`delay()` ставит Celery task в очередь. Функция не выполняется сразу в FastAPI-процессе, ее выполняет Celery worker.

## Что сказать, если спросят "что такое `task_id`?"

Это идентификатор фоновой задачи. По нему можно проверить состояние задачи и получить результат.

## Что сказать, если спросят "какие бывают состояния задачи?"

Основные состояния:

- `PENDING` - задача еще не выполнена или результат неизвестен;
- `STARTED` - задача запущена;
- `SUCCESS` - задача успешно завершилась;
- `FAILURE` - задача завершилась ошибкой.

## Что сказать, если спросят "почему в FastAPI используется `aiohttp`?"

Потому что endpoint объявлен как `async def`. Асинхронный HTTP-клиент не блокирует event loop во время ожидания ответа от parser-service.

## Что сказать, если спросят "почему в Celery task используется `requests`?"

Celery task выполняется в отдельном worker-процессе, не в event loop FastAPI. Поэтому обычный синхронный `requests` здесь допустим.

## Что сказать, если спросят "где сохраняется результат?"

После успешного парсинга результат сохраняется как todo текущего пользователя. В синхронном варианте title идет в `title`, URL идет в `description`. В асинхронном варианте title сохраняется в `title`.

## Что сказать, если спросят "почему нужна авторизация?"

Парсинг создает todo, а todo должен принадлежать конкретному пользователю. Поэтому endpoints парсера используют `UserService.get_current_user` и требуют Bearer token.

## Что сказать, если спросят "как работает база?"

PostgreSQL запускается отдельным контейнером. Tortoise ORM подключается к базе через URL из настроек. При запуске `entrypoint.sh` выполняет `aerich upgrade`, чтобы применить миграции.

## Что сказать, если спросят про threading, multiprocessing и async

`async` - конкурентность в одном потоке, хорошо для сетевого ожидания и I/O. В этой работе используется в FastAPI и `aiohttp`.

`threading` - несколько потоков в одном процессе. Подходит для I/O, но CPU-bound код в Python ограничен GIL.

`multiprocessing` - несколько процессов. Подходит для CPU-bound задач и изоляции выполнения.

Celery worker ближе к отдельному фоновому процессу: он выполняет задачи независимо от FastAPI, поэтому долгий парсинг не блокирует API.

## Что могут попросить найти в коде

Адрес parser-service:

```text
todo-app/todo_app/settings.py
```

Синхронный вызов parser-service:

```text
todo-app/todo_app/api/parser.py
```

Постановка задачи:

```python
tasks.parse_url.delay(...)
```

Получение результата:

```python
celery.result.AsyncResult(task_id)
```

Настройка Celery:

```text
todo-app/todo_app/tasks.py
```

Логика BeautifulSoup:

```text
web-parser/web_parser/utils.py
```

## Возможные замечания и как ответить

### Опечатка `POSTGERS_DB`

В `docker-compose.yaml` у `todo_app` есть:

```yaml
DATABASE_NAME: ${POSTGERS_DB:-todos}
```

Ответ:

> Да, это опечатка в имени переменной окружения. Сейчас приложение работает за счет дефолтного значения `todos`, которое совпадает с базой. В production я бы исправил на `POSTGRES_DB`.

### `requests.post(..., data=parse_request)` в Celery task

Ответ:

> Для более надежной отправки JSON лучше использовать `json=...` или явно поставить `Content-Type: application/json`. В синхронном endpoint это уже сделано через `json=parse_request.model_dump()`.

### Повторный GET результата может создать дубль todo

Ответ:

> Да, сейчас при каждом успешном запросе результата создается todo. Для учебной демонстрации это приемлемо, но в реальном проекте я бы хранил связь `task_id` и результата, чтобы не создавать дубликаты.

### Ошибка в Celery task возвращается строкой

Ответ:

> Сейчас исключение превращается в строку результата. Лучше было бы пробрасывать исключение, чтобы Celery помечал задачу как `FAILURE`.

## Короткий финальный ответ преподавателю

Я выполнил все три подзадачи. Основное FastAPI-приложение, parser-service, PostgreSQL, Redis и Celery worker запускаются через Docker Compose. Парсер доступен как отдельный HTTP-сервис. Основной backend умеет вызывать его синхронно через `/parser/parse` и асинхронно через очередь Celery: `/parser/parse/start` ставит задачу, `/parser/parse/result/{task_id}` возвращает состояние и результат. Результаты парсинга сохраняются в todo текущего пользователя.

