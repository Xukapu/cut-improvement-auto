from fastapi import APIRouter

from app.api.v1.account import router as account_router
from app.api.v1.appointments import router as appointments_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.clients import router as clients_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.disputes import router as disputes_router
from app.api.v1.documents import router as documents_router
from app.api.v1.employees import router as employees_router
from app.api.v1.history import router as history_router
from app.api.v1.notification_management import router as notification_management_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.parts import router as parts_router
from app.api.v1.payments import router as payments_router
from app.api.v1.recommended_works import router as recommended_works_router
from app.api.v1.reports import router as reports_router
from app.api.v1.search import router as search_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.work_items import router as work_items_router
from app.api.v1.work_orders import router as work_orders_router
from app.api.v1.work_participation import router as work_participation_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(account_router)
api_router.include_router(clients_router)
api_router.include_router(vehicles_router)
api_router.include_router(appointments_router)
api_router.include_router(history_router)
api_router.include_router(search_router)
api_router.include_router(work_participation_router)
api_router.include_router(work_orders_router)
api_router.include_router(employees_router)
api_router.include_router(work_items_router)
api_router.include_router(parts_router)
api_router.include_router(recommended_works_router)
api_router.include_router(disputes_router)
api_router.include_router(payments_router)
api_router.include_router(audit_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(documents_router)
api_router.include_router(notifications_router)
api_router.include_router(notification_management_router)
