import strawberry
from typing import List


@strawberry.type
class User:
    id: int
    name: str
    email: str


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from GraphQL!"
    
    @strawberry.field
    def users(self) -> List[User]:
        # Demo data - replace with real data source
        return [
            User(id=1, name="John Doe", email="john@example.com"),
            User(id=2, name="Jane Smith", email="jane@example.com"),
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, email: str) -> User:
        # Demo mutation - replace with real implementation
        return User(id=3, name=name, email=email)


schema = strawberry.Schema(query=Query, mutation=Mutation)
