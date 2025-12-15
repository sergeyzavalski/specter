from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int
    offset: int


def get_pagination_params(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginationParams:
    # customizing - Depends(partial(pagination, limit=Query(200, ge=1, le=500)))
    return PaginationParams(limit=limit, offset=offset)
