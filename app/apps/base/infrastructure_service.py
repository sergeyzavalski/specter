from collections import defaultdict
from functools import wraps
from typing import Callable, Dict

from pydantic import BaseModel
from pypika_tortoise.terms import Term
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Expression, Subquery

from apps.base.models import BaseOrmModel
from apps.base.schemas.requests import PaginationParams
from apps.base.schemas.responses import PaginatedResponseSchema, MetadataSchema

from core.tortoise_orm.pypika_advanced import CountOver
from core.tortoise_orm.utils import Filter


def transform_dict(data: dict) -> dict:
    transformed = {}
    nested = defaultdict(dict)

    for key, value in data.items():
        if "__" in key:
            parent, child = key.split("__", 1)
            nested[parent][child] = value
        else:
            transformed[key] = value

    transformed.update(nested)
    return transformed


def paginate(func: Callable):
    @wraps(func)
    async def wrapper(cls, *args, **kwargs):
        pagination_params: PaginationParams = kwargs.get("pagination")
        models = await func(cls, *args, **kwargs)
        if not pagination_params:
            return models
        if not models:
            return PaginatedResponseSchema(
                data=[],
                meta=MetadataSchema(
                    limit=pagination_params.limit,
                    offset=pagination_params.offset,
                    total_count=0,
                ),
            )
        else:
            if isinstance(models[0], dict):
                try:
                    total_count = models[0]["total_count"]
                except KeyError:
                    total_count = None
                models = [transform_dict(model) for model in models]
            else:
                try:
                    total_count = models[0].total_count
                except AttributeError:
                    total_count = None

        return PaginatedResponseSchema(
            data=models,
            meta=MetadataSchema(
                limit=pagination_params.limit,
                offset=pagination_params.offset,
                total_count=total_count,
            ),
        )

    return wrapper


def data_as_dict(data: dict | BaseModel, exclude_unset: bool = False) -> dict:
    if isinstance(data, BaseModel):
        return data.model_dump(exclude_unset=exclude_unset)
    else:
        return data


class BaseDatabaseTableService:
    __model__: BaseOrmModel = None

    @classmethod
    async def _create(cls, data: BaseModel | dict, **additional_data):
        data = data_as_dict(data)
        return await cls.__model__.create(**data, **additional_data)

    @classmethod
    async def _bulk_create(cls, data: list[BaseModel] | list[dict]):
        await cls.__model__.bulk_create(
            [cls.__model__(**data_as_dict(d)) for d in data]
        )

    @classmethod
    def _get_one_query(
        cls, filter_object: Filter = None, prefetch_related: list[str] = None
    ):
        query = cls.__model__.get()
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if filter_object:
            query = filter_object.filter(query)
        return query

    @classmethod
    async def _get_one(
        cls,
        filter_object: Filter = None,
        prefetch_related: list[str] = None,
        using_db=None,
    ):
        query = cls._get_one_query(
            filter_object=filter_object, prefetch_related=prefetch_related
        )
        model = await query.using_db(using_db)
        return model

    @classmethod
    def _get_all_query(
        cls,
        annotate: Dict[str, Expression | Term] = None,
        filter_object: Filter = None,
        pagination: PaginationParams = None,
        prefetch_related: list[str] = None,
        values: list[str] = None,
    ):
        query = cls.__model__.all()

        if annotate:
            query = query.annotate(**annotate)

        if filter_object:
            query = filter_object.filter(query)
            if hasattr(filter_object, "order_by"):
                query = filter_object.sort(query)

        if filter_object and prefetch_related:
            query = filter_object.prefetch_related(
                query, prefetch_related=prefetch_related
            )
        elif prefetch_related:
            query = query.prefetch_related(*prefetch_related)

        if pagination:
            query = query.annotate(total_count=CountOver())
            query = query.limit(pagination.limit).offset(pagination.offset)

        if filter_object and filter_object.including_values:
            query = filter_object.values(query)
        elif values:
            query = query.values(*values)

        return query

    @classmethod
    async def _get_all(
        cls,
        annotate: Dict[str, Expression | Term] = None,
        filter_object: Filter = None,
        pagination: PaginationParams = None,
        prefetch_related: list[str] = None,
    ):
        query = cls._get_all_query(
            annotate=annotate,
            filter_object=filter_object,
            pagination=pagination,
            prefetch_related=prefetch_related,
        )
        models = await query
        return models

    @classmethod
    async def _bulk_delete(cls, filter_object: Filter, model=None, using_db=None):
        query = model if model else cls.__model__
        query = filter_object.filter(query)
        subquery = Subquery(query.all().values("id"))
        delete_query = model if model else cls.__model__
        count_affected = (
            await delete_query.filter(id__in=subquery).using_db(using_db).delete()
        )
        return count_affected

    @classmethod
    async def _delete_one(cls, filter_object: Filter, returning=False):
        model = await cls._get_one(
            filter_object=filter_object
        )  # проверка что удален будет 1 объект
        count_affected = await cls._bulk_delete(filter_object=filter_object)
        if not count_affected:
            raise DoesNotExist(**filter_object.model_dump())
        elif returning:
            return model
        else:
            return count_affected

    @staticmethod
    async def update_from_dict(model: BaseOrmModel, data: dict | BaseModel):
        model = model.update_from_dict(data_as_dict(data, exclude_unset=True))
        await model.save()

    @classmethod
    async def _update(
        cls,
        filter_object: Filter,
        data: BaseModel | dict,
        returning=False,
        using_db=None,
        one=False,
    ):
        data = data_as_dict(data, exclude_unset=True)
        query = cls.__model__
        query = filter_object.filter(query)
        if using_db:
            query = query.using_db(using_db)
        affected = await query.update(**data)
        if one and not affected:
            raise DoesNotExist(cls.__model__)
        if returning:
            models = await query.all()
            if one:
                return models[0]
            return models
        return affected
