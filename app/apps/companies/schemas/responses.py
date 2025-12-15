from pydantic import BaseModel, Field

from apps.base.schemas.responses import PaginatedResponseSchema


class _Company(BaseModel):
    id: str
    short_description: str
    name: str
    founded_date: int
    employee_count: int

class CompaniesResponse(PaginatedResponseSchema):
    data: list[_Company] = Field(default_factory=list)