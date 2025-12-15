from fastapi_filter import FilterDepends, with_prefix

from core.tortoise_orm.utils import Filter


class _CompanyStatusesFilter(Filter):
    user_id: str | None = None
    liked: bool | None = None
    viewed: bool | None = None

class UserCompaniesFilter(Filter):
    founded_date: int | None = None
    founded_date__gt: int | None = None

    users_statuses: _CompanyStatusesFilter | None = FilterDepends(
        with_prefix("statuses", _CompanyStatusesFilter)
    )