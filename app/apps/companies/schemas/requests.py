from pydantic import BaseModel

from apps.base.schemas.types import SearchField
from apps.companies.models import Company
from core.tortoise_orm.utils import Filter


class CompaniesFilter(Filter):
    total_funding_usd__gte: int | None = None
    total_funding_usd__lte: int | None = None

    founded_date__gte: int | None = None
    founded_date__lte: int | None = None

    employee_count__gte: int | None = None
    employee_count__lte: int | None = None

    short_description__icontains: SearchField | None = None

    order_by: list[str] = None

    class Constants(Filter.Constants):
        model = Company


class UpdateCompanyStatusesSchema(BaseModel):
    liked: bool = None
    viewed: bool = None