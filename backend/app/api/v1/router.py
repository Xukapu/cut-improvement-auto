from fastapi import APIRouter

from app.api.v1.appointments import router as appointments_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.clients import router as clients_router
from app.api.v1.disputes import router as disputes_router
from app.api.v1.employees import router as employees_router
from app.api.v1.history import router as history_router
from app.api.v1.parts import router as parts_router
from app.api.v1.payments import router as payments_router
from app.api.v1.recommended_works import router as recommended_works_router
from app.api.v1.search import router as search_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.work_items import router as work_items_router
from app.api.v1.work_orders import router as work_orders_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(clients_router)
api_router.include_router(vehicles_router)
api_router.include_router(appointments_router)
api_router.include_router(history_router)
api_router.include_router(search_router)
api_router.include_router(work_orders_router)
api_router.include_router(employees_router)
api_router.include_router(work_items_router)

api_router.include_router(parts_router)
api_router.include_router(recommended_works_router)

api_router.include_router(disputes_router)
api_router.include_router(payments_router)
api_router.include_router(audit_router)
