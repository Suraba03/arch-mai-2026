# Лабораторная 2: REST API сервиса доставки (CDEK)

REST API учебного сервиса доставки на FastAPI. Реализует все API из варианта №6:
управление пользователями, посылками и доставками, JWT-аутентификацию, Swagger UI
и OpenAPI-спецификацию.

## Стек

- **Python 3.11**, **FastAPI**, **Pydantic v2**
- **JWT** (`python-jose`) + **bcrypt** для хэша паролей
- **In-memory** хранилище (без БД)
- **pytest** + `httpx`/`TestClient`
- **Docker** + **docker-compose**

## Структура проекта

```
hw02/
├── app/
│   ├── main.py              # FastAPI app, сборка роутеров
│   ├── config.py            # настройки (JWT secret, TTL)
│   ├── auth.py              # JWT, хэш паролей, dependency get_current_user
│   ├── storage.py           # in-memory репозитории
│   ├── models.py            # доменные модели (dataclass)
│   ├── schemas.py           # Pydantic DTO
│   └── routers/
│       ├── auth.py          # /auth/register, /auth/login
│       ├── users.py         # /users/...
│       ├── parcels.py       # /parcels, /users/{id}/parcels
│       └── deliveries.py    # /deliveries/...
├── tests/                   # pytest-тесты
├── scripts/export_openapi.py
├── openapi.yaml             # OpenAPI 3.1 спецификация
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

## Запуск

### Через Docker (рекомендуется)

```bash
docker compose up --build
```

API будет на `http://localhost:8000`, Swagger UI — на `http://localhost:8000/docs`.

### Локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## API

| Метод | URL                                      | Описание                                  | Auth |
|-------|------------------------------------------|-------------------------------------------|:---:|
| POST  | `/auth/register`                         | Регистрация пользователя                  | —   |
| POST  | `/auth/login`                            | Логин (form-data, OAuth2 password flow)   | —   |
| POST  | `/auth/login-json`                       | Логин (JSON-вариант)                      | —   |
| GET   | `/users/by-login/{login}`                | Поиск пользователя по логину              | —   |
| GET   | `/users/search?name=&surname=`           | Поиск по маске имени/фамилии              | —   |
| POST  | `/parcels`                               | Создание посылки от текущего пользователя | ✅  |
| GET   | `/users/{user_id}/parcels`               | Посылки пользователя                      | —   |
| POST  | `/deliveries`                            | Создание доставки от себя к получателю    | ✅  |
| GET   | `/deliveries/by-sender/{user_id}`        | Доставки, где пользователь — отправитель  | —   |
| GET   | `/deliveries/by-recipient/{user_id}`     | Доставки, где пользователь — получатель   | —   |
| GET   | `/health`                                | Проверка живости                          | —   |

### Статус-коды

- `200 OK` — успешный GET
- `201 Created` — успешный POST
- `400 Bad Request` — некорректный запрос (например, нет ни `name`, ни `surname` в поиске)
- `401 Unauthorized` — нет/невалидный JWT
- `403 Forbidden` — попытка отправить чужую посылку
- `404 Not Found` — нет ресурса
- `409 Conflict` — дубликат логина при регистрации
- `422 Unprocessable Entity` — ошибка валидации тела запроса

## Аутентификация

JWT (HS256), время жизни — 60 минут (настраивается через `JWT_EXPIRE_MINUTES`).
Защищены `POST /parcels` и `POST /deliveries`. `sender_id`/`owner_id` всегда берутся
из токена, не из тела запроса.

В Swagger UI кнопка **Authorize** работает через стандартный OAuth2 password flow:
введи `username` (он же `login`) и `password`, остальные поля оставь пустыми.

## Примеры использования (curl)

```bash
# 1. Регистрация
curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"login":"ivan","password":"secret123","first_name":"ivan4","last_name":"Petrov"}'

curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"login":"masha","password":"secret123","first_name":"Masha","last_name":"Sidorova"}'

# 2. Логин и токен
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -F 'username=ivan' -F 'password=secret123' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. Поиск пользователя
curl -s http://localhost:8000/users/by-login/ivan
curl -s "http://localhost:8000/users/search?name=Iv&surname=Petr"

# 4. Создание посылки
curl -s -X POST http://localhost:8000/parcels \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"description":"Книга","weight_kg":1.5}'

# 5. Посылки пользователя
curl -s http://localhost:8000/users/1/parcels

# 6. Создание доставки
RECIPIENT_ID=$(curl -s http://localhost:8000/users/by-login/masha \
  | python -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -s -X POST http://localhost:8000/deliveries \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"parcel_id\":1,\"recipient_id\":$RECIPIENT_ID}"

# 7. Доставки по отправителю/получателю
curl -s http://localhost:8000/deliveries/by-sender/1
curl -s http://localhost:8000/deliveries/by-recipient/$RECIPIENT_ID
```

## OpenAPI-спецификация

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON: `http://localhost:8000/openapi.json`
- Файл в репозитории: [`openapi.yaml`](./openapi.yaml)

Перегенерация YAML:

```bash
python -m scripts.export_openapi
```

## Тесты

```bash
pytest -v
```

Тесты покрывают:
- регистрацию/логин (успех, дубликат, неверный пароль, валидация);
- поиск пользователей (по логину, по маске, отсутствие параметров);
- создание посылки (без токена, с токеном, валидация, список посылок, 404);
- создание доставки (успех, без токена, самому себе, чужая посылка, 404 по посылке/получателю);
- получение доставок по отправителю/получателю.

Каждый тест работает на чистом in-memory хранилище (фикстура автоматически
сбрасывает состояние).

## Переменные окружения

| Переменная           | По умолчанию          | Назначение                |
|----------------------|-----------------------|---------------------------|
| `JWT_SECRET`         | `dev-secret-change-me`| Секрет для подписи JWT    |
| `JWT_ALGORITHM`      | `HS256`               | Алгоритм подписи          |
| `JWT_EXPIRE_MINUTES` | `60`                  | Время жизни access-токена |

## Описание варианта (ДЗ)

Вариант №6 — Сервис доставки (https://www.cdek.ru/ru/).

Сущности:
- **Пользователь** (`id`, `login`, `password_hash`, `first_name`, `last_name`)
- **Посылка** (`id`, `owner_id`, `description`, `weight_kg`, `created_at`)
- **Доставка** (`id`, `parcel_id`, `sender_id`, `recipient_id`, `status`, `created_at`)

Все API из задания реализованы (см. таблицу выше).