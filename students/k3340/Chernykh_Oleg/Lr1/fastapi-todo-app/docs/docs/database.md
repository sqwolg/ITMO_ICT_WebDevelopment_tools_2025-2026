# Модели и база данных

## ORM

Для работы с базой данных используется Tortoise ORM. Подключение регистрируется в `todo_app/app.py`:

```python
register_tortoise(
    app,
    db_url=settings.db_url,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
```

Параметр `generate_schemas=True` позволяет автоматически создать таблицы при запуске приложения.

## User

Модель пользователя содержит:

| Поле | Тип | Назначение |
| --- | --- | --- |
| `id` | `IntField` | Первичный ключ |
| `username` | `CharField` | Уникальное имя пользователя |
| `password` | `CharField` | Хэш пароля |
| `created_at` | `DatetimeField` | Дата создания |

Пароль исключается из Pydantic-представления через `PydanticMeta`.

## Todo

Модель задачи содержит:

| Поле | Тип | Назначение |
| --- | --- | --- |
| `id` | `IntField` | Первичный ключ |
| `title` | `CharField` | Заголовок задачи |
| `description` | `CharField` | Описание |
| `is_completed` | `BooleanField` | Статус выполнения |
| `updated_at` | `DatetimeField` | Дата обновления |
| `owner` | `ForeignKeyField` | Связь с пользователем |

Связь `owner` ограничивает доступ к задачам: пользователь может изменять и удалять только свои todo.

## Безопасность

Пароль хэшируется через `bcrypt`. JWT создается с полями `sub`, `iat` и `exp`, где `sub` хранит идентификатор пользователя. Срок действия токена задается настройкой `jwt_token_expiration`.
