# Запуск

## Зависимости

Зависимости перечислены в `requirements.txt`:

```text
fastapi
pydantic
uvicorn
tortoise-orm
bcrypt
python-dotenv
python-jose
python-multipart
```

## Переменные окружения

Приложение читает настройки из `.env`. Минимально нужны:

```env
DATABASE_URL=sqlite://db.sqlite3
SECRET_KEY=change-me
JWT_ALGORITHM=HS256
```

Также в `settings.py` заданы параметры запуска:

| Настройка | Значение по умолчанию |
| --- | --- |
| `server_host` | `localhost` |
| `server_port` | `8000` |
| `reload` | `True` |
| `workers` | `4` |
| `jwt_token_expiration` | `1800` |

## Команды

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск из папки `todo_app`:

```bash
python run.py
```

После запуска Swagger UI доступен по адресу:

```text
http://localhost:8000/docs
```

## Проверка сценария

1. Создать пользователя через `POST /users/`.
2. Получить token через `POST /users/token`.
3. Нажать `Authorize` в Swagger UI и указать Bearer token.
4. Создать todo через `POST /todos/`.
5. Получить список своих задач через `GET /todos/my`.
