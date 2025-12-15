from apps.base.infrastructure_service import BaseDatabaseTableService
from apps.companies.schemas.requests import UpdateCompanyStatusesSchema
from apps.users.models import UserCompanyStatus


class UserCompanyStatusTableService(BaseDatabaseTableService):
    @classmethod
    async def update(
        cls, company_id, user_id, data: UpdateCompanyStatusesSchema
    ):
        await UserCompanyStatus.filter(company_id=company_id, user_id=user_id).update(**data.model_dump())
