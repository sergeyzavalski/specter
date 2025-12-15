from apps.companies.schemas.requests import UpdateCompanyStatusesSchema
from apps.companies.services.infrastructure import CompaniesTableService
from apps.users.services.infrastructure import UserCompanyStatusTableService


async def all_companies(filter_object, pagination):
    return await CompaniesTableService.all(
        filter_object=filter_object,
        pagination=pagination
    )


async def update_company_statuses(company_id, user_id, data: UpdateCompanyStatusesSchema):
    await UserCompanyStatusTableService.update(
        company_id=company_id, user_id=user_id, data=data
    )