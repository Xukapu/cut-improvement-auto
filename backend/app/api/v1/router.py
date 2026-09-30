from fastapi import APIRouter

from app.api.v1.appointments import router as appointments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.clients import router as clients_router
from app.api.v1.history import router as history_router
from app.api.v1.search import router as search_router
from app.api.v1.vehicles import router as vehicles_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(clients_router)
api_router.include_router(vehicles_router)
api_router.include_router(appointments_router)
api_router.include_router(history_router)
api_router.include_router(search_router)
