import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class LocaleType:
    id: int
    key: str
    value: str
    language: str
    namespace: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


@strawberry.input
class LocaleCreateInput:
    key: str
    value: str
    language: str
    namespace: str = "default"
    is_active: bool = True


@strawberry.input
class LocaleUpdateInput:
    key: Optional[str] = None
    value: Optional[str] = None
    language: Optional[str] = None
    namespace: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class LocaleFilter:
    language: Optional[str] = None
    namespace: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class LocaleConnection:
    edges: List[strawberry.relay.Edge[LocaleType]]
    page_info: strawberry.relay.PageInfo


@strawberry.type
class DeleteResponse:
    success: bool
    message: str
