from fastapi import APIRouter
from apps.companies.views import router as companies_router
router = APIRouter()

router.include_router(
    companies_router,
    prefix="/companies",
)
