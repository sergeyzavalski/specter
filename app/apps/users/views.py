from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends

from apps.base.schemas.requests import get_pagination_params, PaginationParams
from apps.users.schemas.requests import UserCompaniesFilter
from apps.users.schemas.responses import UsersCompaniesResponse
from apps.users.services.business import all_user_companies

router = APIRouter()

@router.get(
    "/{user_id}/companies-statuses",
    status_code=200,
)
async def filter_user_companies_statuses_view(
    user_id: str,
    filter_object: UserCompaniesFilter = FilterDepends(UserCompaniesFilter),
    pagination_params: PaginationParams = Depends(get_pagination_params),
) -> UsersCompaniesResponse:
    filter_object.users_statuses.user_id = user_id  # from auth in real
    companies = await all_user_companies(
        filter_object=filter_object,
        pagination=pagination_params,
    )
    return companies
