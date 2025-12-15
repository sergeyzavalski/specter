import uvicorn
from pydantic import BaseModel
from starlette import status

from application import create_app
from core.settings import get_settings

settings = get_settings()
app = create_app()
class HealthCheck(BaseModel):
    status: str = "OK"

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    return HealthCheck(status="OK")

if __name__ == "__main__":
    uvicorn.run(
        "__main__:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        # log_config=None,
    )
