from tortoise import Model
from tortoise.fields import ReverseRelation, IntField, CharField, BooleanField, ForeignKeyField


class User(Model):
    id: int = IntField(primary_key=True)
    userid: str = CharField(max_length=32, unique=True)

    companies_statuses: ReverseRelation["UserCompanyStatus"]


class UserCompanyStatus(Model):
    liked: bool | None = BooleanField(default=None, null=True)
    viewed: bool = BooleanField(default=False)

    company = ForeignKeyField("models.Company", related_name="users_statuses") #  only for SQL query purposes
    user: "User" = ForeignKeyField("models.User", related_name="company_statuses", to_field="userid")

    class Meta:
        table = "user_company_status"
        unique_together = ("company_id", "user_id")