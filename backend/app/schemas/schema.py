import strawberry
from app.resolvers.locale_resolver import LocaleQuery, LocaleMutation


@strawberry.type
class Query(LocaleQuery):
    pass


@strawberry.type
class Mutation(LocaleMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
