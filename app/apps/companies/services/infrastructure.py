from apps.base.infrastructure_service import BaseDatabaseTableService, paginate
from apps.base.schemas.requests import PaginationParams
from apps.companies.models import Company
from apps.users.schemas.requests import UserCompaniesFilter
from utils.clickhouse_client import clickhouse_client


class CompaniesTableService(BaseDatabaseTableService):

    __model__ = Company
    @classmethod
    @paginate
    async def all(
        cls,
        filter_object: UserCompaniesFilter,
        pagination: PaginationParams | None,
    ) -> list[Company]:
        query = cls._get_all_query(
            filter_object=filter_object,
            pagination=pagination
        )
        query = query.sql(params_inline=True).replace("ESCAPE '\\'", "")
        return await clickhouse_client.execute(query)
