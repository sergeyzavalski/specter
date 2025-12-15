import csv
from pathlib import Path

from tortoise import BaseDBAsyncClient

from core.settings import get_settings
from utils.clickhouse_client import clickhouse_client

async def upgrade(db: BaseDBAsyncClient) -> str:
    insert_query = """
    INSERT INTO "user" (id, userid)
        VALUES ($1, $2)
        ON CONFLICT (userid) DO NOTHING;
    """
    batch = []
    with open(Path(__file__).resolve().with_name("specter_fake_users.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append([int(row["id"]), row["userid"]])

    await db.execute_many(insert_query, batch)

    insert_query = """
    INSERT INTO user_company_status
        (user_id, company_id, viewed, liked)
        VALUES ($1, $2, $3, $4)
    ON CONFLICT (company_id, user_id) DO NOTHING;
    """
    batch = []
    with open(Path(__file__).resolve().with_name("specter_fake_users_company_statuses.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append(
                [
                    row["user_id"],
                    row["company_id"],
                    bool(row["viewed"]) if row["viewed"] != "" else False,
                    bool(row["liked"]) if row["liked"] != "" else None,
                ]
            )
    await db.execute_many(insert_query, batch)

    return "SELECT 1 FROM aerich"


async def downgrade(db: BaseDBAsyncClient) -> str:
    return ""
