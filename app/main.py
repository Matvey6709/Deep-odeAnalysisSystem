from fastapi import FastAPI

from app.routers import analytics, devices, users


app = FastAPI(
    title="Device Stats Service",
    description="Сбор и анализ статистики с устройств. Аналитика считается асинхронно через Celery.",
    version="0.1.0",
)

app.include_router(users.router)
app.include_router(devices.router)
app.include_router(analytics.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
