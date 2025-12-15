from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends

from apps.base.schemas.requests import PaginationParams, get_pagination_params
from apps.companies.schemas.requests import CompaniesFilter, UpdateCompanyStatusesSchema
from apps.companies.schemas.responses import CompaniesResponse
from apps.companies.services.business import all_companies, update_company_statuses

router = APIRouter()

@router.get(
    "",
    status_code=200,
)
async def filter_companies_view(
    filter_object: CompaniesFilter = FilterDepends(CompaniesFilter),
    pagination_params: PaginationParams = Depends(get_pagination_params),
) -> CompaniesResponse:
    companies = await all_companies(
        filter_object=filter_object,
        pagination=pagination_params,
    )
    return companies


@router.patch(
    "/{company_id}/{user_id}/statuses",
    status_code=204,
)
async def update_company_view(
    company_id: str,
    user_id: str,
    data: UpdateCompanyStatusesSchema,
):
    await update_company_statuses(
        company_id=company_id,
        user_id=user_id, # from auth in real
        data=data,
    )