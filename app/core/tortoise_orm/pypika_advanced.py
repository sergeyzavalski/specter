from pypika_tortoise.terms import AnalyticFunction
from tortoise.expressions import Expression, ResolveResult


class CountOver(Expression):
    def resolve(self, *args, **kwargs):
        return ResolveResult(term=AnalyticFunction("COUNT(*) OVER"))