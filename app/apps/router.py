from fastapi import APIRouter

from apps.companies.router import router as companies_router
from apps.users.router import router as users_router

router = APIRouter()


router.include_router(
    users_router,
    tags=["Users module"],
)

router.include_router(
    companies_router,
    tags=["Companies module"],
)
