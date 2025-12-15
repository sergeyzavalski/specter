from typing import Optional, Union, List, Any, Dict

from clickhouse_connect import get_async_client
from clickhouse_connect.driver import AsyncClient
import structlog
import time

from core.settings import get_settings

settings = get_settings()
logger = structlog.stdlib.get_logger(__name__)


class ClickHouseClient:
    client: Optional[AsyncClient] = None

    @classmethod
    async def start(
        cls,
        host: str = settings.clickhouse.HOST,
        port: int = settings.clickhouse.PORT,
        username: str = settings.clickhouse.USER,
        password: str = settings.clickhouse.PASS,
        database: str = settings.clickhouse.NAME,
        secure: bool = settings.clickhouse.SECURE,
        verify: bool = settings.clickhouse.VERIFY,
        ca_cert: str | None = settings.clickhouse.CA_CERT,
    ) -> None:
        # Reuse existing client if already started
        if cls.client is not None:
            return
        cls.client = await get_async_client(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            connect_timeout=30,
            send_receive_timeout=3600,
            secure=secure,
            verify=verify,
            ca_cert=ca_cert,
        )

    @classmethod
    async def stop(cls) -> None:
        if cls.client:
            await cls.client.close()
            cls.client = None

    async def execute(
        self, query: str, parameters: Optional[dict] = None, *args, **kwargs
    ) -> Union[int, List[Dict[str, Any]]]:
        if self.client is None:
            raise RuntimeError("ClickHouse client is not started")
        start_ns = time.perf_counter_ns()
        result = await self.client.query(query, parameters=parameters, *args, **kwargs)
        duration_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
        is_select = query.lstrip().upper().startswith("SELECT")
        if not is_select:
            written_rows = result.summary.get("written_rows", 0)
            logger.info(
                "clickhouse.execute",
                sql=query,
                params=parameters or {},
                duration=f"{duration_ms:.3f} ms",
                written_rows=written_rows,
            )
            return written_rows
        rows = result.result_rows or []
        columns = result.column_names or []
        mapped = [dict(zip(columns, row)) for row in rows]
        logger.info(
            "clickhouse.execute",
            sql=query,
            params=parameters or {},
            duration=f"{duration_ms:.3f} ms",
            row_count=len(mapped),
        )
        return mapped


clickhouse_client = ClickHouseClient()
