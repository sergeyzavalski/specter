import asyncio  # noqa: I001
from contextlib import asynccontextmanager

import aerich
from fastapi import FastAPI

from apps.router import router
from core.settings import get_settings
from core.tortoise_orm.config import DB_CONFIG
from utils.clickhouse_client import clickhouse_client


settings = get_settings()


def create_app():
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        aerich_command = aerich.Command(
            tortoise_config=DB_CONFIG, location="./core/aerich/migrations"
        )
        await aerich_command.init()
        await aerich_command.upgrade(run_in_transaction=True)

        await clickhouse_client.start()
        yield
        await clickhouse_client.stop()

    app = FastAPI(
        redoc_url=None,
        openapi_url="/openapi.json" if settings.app.SWAGGER else None,
        docs_url="/swagger/" if settings.app.SWAGGER else None,
        lifespan=lifespan,
    )
    app.include_router(router)

    return app
