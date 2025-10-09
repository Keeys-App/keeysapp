import strawberry
from typing import Optional
from app.schemas.auth import AuthQuery, AuthMutation, UserType


@strawberry.type
class Query:
    """
    Root GraphQL Query.
    """
    
    @strawberry.field
    def hello(self) -> str:
        """
        Simple hello query for testing.
        """
        return "Hello from GraphQL!"
    
    # Include auth queries
    me: Optional[UserType] = strawberry.field(resolver=AuthQuery.me)


@strawberry.type
class Mutation:
    """
    Root GraphQL Mutation.
    """
    
    # Include auth mutations
    register = strawberry.field(resolver=AuthMutation.register)
    login = strawberry.field(resolver=AuthMutation.login)


schema = strawberry.Schema(query=Query, mutation=Mutation)
