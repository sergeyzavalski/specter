from pydantic import BaseModel, Field

from apps.base.schemas.responses import PaginatedResponseSchema


class _UserCompany(BaseModel):
    id: str
    short_description: str
    name: str
    founded_date: int
    employee_count: int


class UsersCompaniesResponse(PaginatedResponseSchema):
    data: list[_UserCompany] = Field(default_factory=list)