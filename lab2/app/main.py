from fastapi import FastAPI

from app.routers import auth as auth_router
from app.routers import deliveries as deliveries_router
from app.routers import parcels as parcels_router
from app.routers import users as users_router


app = FastAPI(
    title="CDEK-like Delivery API",
    version="0.1.0",
    description="Учебный сервис доставки. ДЗ-2 по курсу «Архитектура программных систем».",
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(parcels_router.router)
app.include_router(deliveries_router.router)


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}