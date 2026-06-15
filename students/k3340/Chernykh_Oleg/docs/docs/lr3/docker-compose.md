# Docker Compose

## Сервисы

В `docker-compose.yaml` описаны пять основных сервисов.

| Сервис | Назначение |
| --- | --- |
| `postgres` | Хранит данные приложения |
| `todo_app` | Основной FastAPI backend |
| `web_parser` | HTTP-сервис для парсинга URL |
| `redis` | Брокер Celery и backend результатов |
| `celery_worker` | Выполняет фоновые задачи |

## PostgreSQL

PostgreSQL запускается из образа `postgres:15-alpine`. Для сохранения данных используется volume `postgres_data`. Healthcheck через `pg_isready` помогает дождаться готовности базы перед запуском зависимых сервисов.

## todo_app

Основное приложение собирается из папки `todo-app`. В контейнер передаются переменные окружения для подключения к базе данных, Redis и сервису парсера.

Порт `8000` проброшен наружу, поэтому документация FastAPI доступна с хоста:

```text
http://localhost:8000/docs
```

Перед стартом API `entrypoint.sh` применяет миграции через Aerich, затем запускает приложение.

## web_parser

Парсер собирается из папки `web-parser`. Он доступен внутри Docker-сети по имени сервиса:

```text
http://web_parser:8000/parse
```

Основному приложению не нужен внешний IP парсера: Docker Compose автоматически добавляет DNS-имена сервисов в общую сеть.

## Redis и Celery worker

Redis запускается как отдельный контейнер и защищается паролем. Celery worker собирается из кода `todo-app`, но стартует отдельной командой:

```text
poetry run celery -A todo_app.tasks worker --loglevel=info
```

Worker слушает очередь Redis, получает задачу парсинга, вызывает `web_parser` и сохраняет результат.

## Запуск

Из папки лабораторной:

```bash
docker compose up --build
```

После запуска можно открыть Swagger UI основного приложения:

```text
http://localhost:8000/docs
```
