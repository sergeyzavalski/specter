from typing import Any

from pydantic import BaseModel


class MetadataSchema(BaseModel):
    limit: int
    offset: int
    total_count: int | None = None

class PaginatedResponseSchema(BaseModel):
    meta: MetadataSchema
    data: list[Any]