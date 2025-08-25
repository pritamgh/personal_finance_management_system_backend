from fastapi import APIRouter

from src.admin.views import router as admin_router
from src.budget.views import router as budget_router
from src.dashboard.views import router as dashboard_router
from src.stat.views import router as stat_router
from src.transaction.views import router as transaction_router
from src.user.views import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/api/v1/user", tags=["user"])
api_router.include_router(
    transaction_router, prefix="/api/v1/transaction", tags=["transaction"]
)
api_router.include_router(budget_router, prefix="/api/v1/budget", tags=["budget"])
api_router.include_router(stat_router, prefix="/api/v1/stat", tags=["stat"])
api_router.include_router(
    dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"]
)
api_router.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
