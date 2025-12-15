from fastapi import APIRouter
from apps.users.views import router as users_router
router = APIRouter()

router.include_router(
    users_router,
    prefix="/users",
)
