# Device Stats Service

Сервис учёта и анализа данных, поступающих с условных устройств. Данные
вида `{x, y, z}` привязываются к устройству и временной метке, складываются в
PostgreSQL и затем по запросу анализируются (min/max/count/sum/median).

Аналитика считается **асинхронно** в Celery-воркере: запрос на расчёт ставится
в очередь Redis, а клиент получает `task_id` и опрашивает `/tasks/{id}`.

## Стек

- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (sync) + Alembic
- PostgreSQL 16
- Celery 5 + Redis 7
- Locust для нагрузочного теста
- Docker + docker-compose

## Структура

```
app/
  main.py            FastAPI-приложение, подключение роутеров
  config.py          настройки из env
  database.py        engine + SessionLocal + Base
  models.py          User, Device, Statistic
  schemas.py         Pydantic-схемы
  crud.py            операции с БД
  analytics.py       SQL-агрегации min/max/count/sum/median
  celery_app.py      инстанс Celery
  tasks.py           celery-таски аналитики
  routers/
    users.py
    devices.py
    analytics.py
alembic/             миграции
locustfile.py        сценарий нагрузочного теста
Dockerfile
docker-compose.yml
```

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

Поднимутся 4 сервиса: `db`, `redis`, `api` (миграции применяются автоматически
при старте), `worker`.

## API

| Метод | Путь | Назначение |
|---|---|---|
| `POST` | `/users` | создать пользователя |
| `GET` | `/users` | список пользователей |
| `GET` | `/users/{user_id}` | пользователь по id |
| `GET` | `/users/{user_id}/devices` | устройства пользователя |
| `POST` | `/devices` | создать устройство (опционально `user_id`) |
| `GET` | `/devices` | список устройств, фильтр `?user_id=` |
| `GET` | `/devices/{device_id}` | устройство по id |
| `POST` | `/devices/{device_id}/statistics` | положить отсчёт `{x, y, z}` |
| `GET` | `/devices/{device_id}/statistics` | последние отсчёты, фильтры `start`/`end`/`limit` |
| `POST` | `/devices/{device_id}/analytics` | поставить задачу аналитики по устройству |
| `POST` | `/users/{user_id}/analytics` | поставить задачу аналитики по пользователю |
| `GET` | `/tasks/{task_id}` | статус/результат задачи Celery |

Фильтры по времени: `start` и `end` принимают ISO-8601, оба необязательны.

## Нагрузочное тестирование (Locust)

`locustfile.py` моделирует устройство, которое часто шлёт отсчёты и иногда
запрашивает аналитику (соотношение задач 20 : 2 : 1 — записать / аналитика по
устройству / аналитика по пользователю).

### Запуск через compose

```bash
docker compose --profile loadtest up -d locust
# http://localhost:8089
```


