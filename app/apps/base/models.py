from tortoise import Model


class BaseOrmModel(Model):
    class Meta:
        abstract = True
