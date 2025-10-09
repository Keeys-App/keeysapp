from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LocaleBase(BaseModel):
    key: str
    value: str
    language: str
    namespace: str = "default"
    is_active: bool = True


class LocaleCreate(LocaleBase):
    pass


class LocaleUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    language: Optional[str] = None
    namespace: Optional[str] = None
    is_active: Optional[bool] = None


class LocaleResponse(LocaleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
