from tortoise import Model
from tortoise.fields import CharField, ReverseRelation, IntField

from apps.users.models import UserCompanyStatus


class Company(Model):
    # ClickHouse table
    id: str = CharField(primary_key=True, max_length=24) # uuid.uuid4().hex
    name: str = CharField(max_length=256)
    domain: str = CharField(max_length=256)
    founded_date: int = IntField()
    short_description: str = CharField(max_length=256)
    total_funding_usd: int = IntField()
    employee_count: int = IntField()

    statuses: ReverseRelation["UserCompanyStatus"]  #  only for building SQL query purposes

    class Meta:
        table = "company"