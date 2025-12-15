from apps.companies.services.infrastructure import CompaniesTableService


async def all_user_companies(filter_object, pagination):
    return await CompaniesTableService.all(
        filter_object=filter_object,
        pagination=pagination
    )
