import csv
from pathlib import Path

from tortoise import BaseDBAsyncClient

from core.settings import get_settings
from utils.clickhouse_client import clickhouse_client

settings = get_settings()


async def upgrade_clickhouse():
    await clickhouse_client.start()
    host_with_port = f'{settings.postgres_api.HOST}:{settings.postgres_api.PORT}'
    username = settings.postgres_api.USER
    password = settings.postgres_api.PASS
    database = settings.postgres_api.NAME
    postgres_engine = f"PostgreSQL('{host_with_port}', '{database}', {{}}, '{username}', '{password}')"
    await clickhouse_client.execute("DROP TABLE IF EXISTS default.company;")
    migration = f"""
                CREATE TABLE default.company
                (
                    "id"                String  NOT NULL PRIMARY KEY,
                    "name"              String NOT NULL,
                    "domain"            String NOT NULL,
                    "founded_date"      Int32 ,
                    "short_description" String NOT NULL,
                    "total_funding_usd" Int32          ,
                    "employee_count"     Int32          NOT NULL
                );
                """
    await clickhouse_client.execute(migration)
    await clickhouse_client.execute("DROP TABLE IF EXISTS default.user_company_status;")
    migration = f"""
                CREATE TABLE default.user_company_status
                (
                    "id"         Int32,
                    "liked"      BOOL,
                    "viewed"     BOOL        NOT NULL,
                    "company_id" String NOT NULL,
                    "user_id"    String NOT NULL,
                )
                    engine = {postgres_engine.format('user_company_status')}
                """
    await clickhouse_client.execute(migration)

    query = """
    INSERT INTO default.company
    (
        id,
        name,
        domain,
        founded_date,
        short_description,
        total_funding_usd,
        employee_count
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """


    with open(Path(__file__).resolve().with_name("companies.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f.read().splitlines())
        for row in reader:
            await clickhouse_client.execute(
                query,
                (
                    row["company_id"],
                    row["company_name"],
                    row["domain"],
                    int(row["founded_date"]) if row["founded_date"] else None,
                    row["short_description"],
                    int(row["total_funding_usd"]) if row["total_funding_usd"] else None,
                    int(row["employee_count"]) if row["employee_count"] else None,
                ),
            )

async def upgrade(db: BaseDBAsyncClient) -> str:
    await upgrade_clickhouse()
    return """
            DROP TABLE IF EXISTS "user_company_status";
            DROP TABLE IF EXISTS "user";
            CREATE TABLE "user"
            (
                "id"     SERIAL      NOT NULL PRIMARY KEY,
                "userid" VARCHAR(32) NOT NULL UNIQUE
            );
                
           CREATE TABLE IF NOT EXISTS "user_company_status"
           (
               "id"         SERIAL      NOT NULL PRIMARY KEY,
               "liked"      BOOL,
               "viewed"     BOOL        DEFAULT FALSE,
               "company_id" VARCHAR(24) NOT NULL, --REFERENCES "company" ("id") ON DELETE CASCADE,
               "user_id"    VARCHAR(32) NOT NULL REFERENCES "user" ("userid") ON DELETE CASCADE,
               CONSTRAINT "uid_user_compan_company_d18969" UNIQUE ("company_id", "user_id")
           );
           CREATE TABLE IF NOT EXISTS "aerich"
           (
               "id"      SERIAL       NOT NULL PRIMARY KEY,
               "version" VARCHAR(255) NOT NULL,
               "app"     VARCHAR(100) NOT NULL,
               "content" JSONB        NOT NULL
           );
           """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
