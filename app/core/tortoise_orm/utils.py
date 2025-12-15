from collections import defaultdict
from functools import reduce
from operator import or_
from typing import Annotated

from fastapi_filter.base.filter import BaseFilterModel
from pydantic import AfterValidator, field_validator, ValidationInfo
from tortoise import Model, Tortoise
from tortoise.queryset import Q, QuerySet


def find_underscore_after_double(s: str) -> str | None:
    last_double = s.rfind("__")
    if last_double == -1:
        return None
    return s[0:last_double]

orm_operator_transformer = {
    "neq": lambda value: ("__not", value),
    "gt": lambda value: ("__gt", value),
    "gte": lambda value: ("__gte", value),
    "in": lambda value: ("__in", value),
    "isnull": lambda value: ("__isnull", True),
    "lt": lambda value: ("__lt", value),
    "lte": lambda value: ("__lte", value),
    "like": lambda value: ("__contains", value),
    "ilike": lambda value: ("__icontains", value),
    "not": lambda value: ("__not", value),
    "not_in": lambda value: ("__not_in", value),
}


class Filter(BaseFilterModel):
    or_conditions_list: Annotated[list[dict], AfterValidator(lambda x: None)] = (
        None  # невозможно использовать на FE
    )

    class Constants(BaseFilterModel.Constants):
        include_fields_field_name: str = "include_fields"
        or_conditions_field_name: str = "or_conditions_list"

    @property
    def filtering_fields(self):
        fields = self.model_dump(exclude_none=True, exclude_unset=True)
        fields.pop(self.Constants.ordering_field_name, None)
        return fields.items()

    @field_validator("*", mode="before")
    def split_str(cls, value, field: ValidationInfo):
        if (
            field.field_name is not None
            and (
                field.field_name == cls.Constants.ordering_field_name
                or field.field_name == cls.Constants.include_fields_field_name
                or field.field_name.endswith("__in")
                or field.field_name.endswith("__not_in")
            )
            and isinstance(value, str)
        ):
            if not value:
                # Empty string should return [] not ['']
                return []
            return list(value.split(","))
        return value

    def _or_filters_list_to_dict(
        self, or_conditions: "Filter", parent_field_name: str = "", result=None
    ) -> dict:
        if result is None:
            result = {}

        for field_name, value in or_conditions.filtering_fields:
            field_value = getattr(or_conditions, field_name)

            if isinstance(field_value, Filter):
                self._or_filters_list_to_dict(field_value, field_name, result)

            else:
                if "__" in field_name:
                    try:
                        operator, value = orm_operator_transformer[
                            field_name.rsplit("__", maxsplit=1)[-1]
                        ](value)
                        field_name = field_name.rsplit("__", maxsplit=1)[0]
                    except KeyError:
                        operator = ""
                else:
                    operator = ""
                _parent_field_name = (
                    parent_field_name + "__" if parent_field_name else ""
                )
                result[f"{_parent_field_name}{field_name}{operator}"] = value

        return result

    def filter(
        self,
        query: QuerySet | QuerySet[Model],
        parent_field_name: str = "",
        skip_icontains: bool = False,
    ):
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name)
            if isinstance(field_value, Filter):
                _parent_field_name = (
                    parent_field_name + "__" if parent_field_name else ""
                )
                field_name = f"{_parent_field_name}{field_name}"
                query = field_value.filter(query, field_name)
            else:
                if "__" in field_name:
                    try:
                        operator, value = orm_operator_transformer[
                            field_name.rsplit("__", maxsplit=1)[-1]
                        ](value)
                        field_name = field_name.rsplit("__", maxsplit=1)[0]
                    except KeyError:
                        operator = ""

                else:
                    operator = ""

                if (
                    field_name == self.Constants.search_field_name
                    and hasattr(self.Constants, "search_model_fields")
                    and not skip_icontains
                ):
                    search_filters = [
                        {f"{field}__icontains": value}
                        for field in self.Constants.search_model_fields
                        if value
                    ]
                    query = query.filter(
                        reduce(or_, [Q(**filt) for filt in search_filters])
                    )
                elif field_name == self.Constants.or_conditions_field_name:
                    for or_conditions in self.or_conditions_list:
                        subquery = Q()
                        _parent_field_name = (
                            parent_field_name + "__" if parent_field_name else ""
                        )
                        for k, v in or_conditions.items():
                            _filters = {f"{_parent_field_name}{k}": v}
                            self._add_extra_filters(
                                _filters, f"{_parent_field_name}{k}"
                            )
                            subquery |= Q(**_filters)
                        query = query.filter(subquery)
                elif field_name == self.Constants.ordering_field_name:
                    continue
                elif field_name != self.Constants.include_fields_field_name:
                    _parent_field_name = (
                        parent_field_name + "__" if parent_field_name else ""
                    )
                    _filters = {f"{_parent_field_name}{field_name}{operator}": value}

                    self._add_extra_filters(_filters, field_name)

                    query = query.filter(**_filters)

        return query

    @staticmethod
    def _add_extra_filters(filters: dict, field_name: str): ...

    def sort(self, query: QuerySet):
        if not self.ordering_values:
            return query

        return query.order_by(*self.ordering_values)

    @property
    def including_values(self):
        return getattr(self, self.Constants.include_fields_field_name, None)

    def prefetch_related(self, query: QuerySet, prefetch_related: list[str]):
        if self.including_values:
            overriden_prefetch_related = set()
            for prefetch_field in self.including_values:
                if field := find_underscore_after_double(prefetch_field):
                    overriden_prefetch_related.add(field)
            query = query.prefetch_related(*overriden_prefetch_related)
        else:
            query = query.prefetch_related(*prefetch_related)
        return query

    def values(self, query: QuerySet):
        if self.including_values:
            query = query.values(*self.including_values, *query._annotations)
        return query

    @field_validator("*", mode="before", check_fields=False)
    def validate_order_by(cls, value, field: ValidationInfo):
        if field.field_name != cls.Constants.ordering_field_name:
            return value

        if not value:
            return None

        field_name_usages = defaultdict(list)
        duplicated_field_names = set()

        for field_name_with_direction in value:
            field_name = field_name_with_direction.replace("-", "").replace("+", "")

            try:
                cls._check_field_exist(cls.Constants.model, field_name)
            except ValueError:
                raise ValueError(f"{field_name} is not a valid ordering field.")

            field_name_usages[field_name].append(field_name_with_direction)
            if len(field_name_usages[field_name]) > 1:
                duplicated_field_names.add(field_name)

        if duplicated_field_names:
            ambiguous_field_names = ", ".join(
                [
                    field_name_with_direction
                    for field_name in sorted(duplicated_field_names)
                    for field_name_with_direction in field_name_usages[field_name]
                ]
            )
            raise ValueError(
                f"Field names can appear at most "
                f"once for {cls.Constants.ordering_field_name}. "
                f"The following was ambiguous: {ambiguous_field_names}."
            )

        return value

    @classmethod
    def _check_field_exist(cls, model, field_name: str):
        if "__" in field_name:
            fk_field, related_model_field = field_name.split("__", 1)

            if (
                fk_field not in model._meta.fk_fields
                and fk_field not in model._meta.m2m_fields
            ):
                raise ValueError()

            related_model = cls._get_model_by_fk_field(model, fk_field)

            return cls._check_field_exist(related_model, related_model_field)

        if field_name not in model._meta.db_fields and field_name not in getattr(
            model.Meta, "agg_fields", []
        ):
            raise ValueError()

    @staticmethod
    def _get_model_by_fk_field(model, fk_field: str):
        tort_app, tort_model = model._meta.fields_map[fk_field].model_name.split(".")
        related_model = Tortoise.apps[tort_app][tort_model]
        return related_model
