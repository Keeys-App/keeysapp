import strawberry
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.locale import Locale
from app.schemas.graphql import (
    LocaleType, 
    LocaleCreateInput, 
    LocaleUpdateInput, 
    LocaleFilter,
    DeleteResponse
)


def locale_model_to_type(locale: Locale) -> LocaleType:
    """Convert SQLAlchemy model to GraphQL type"""
    return LocaleType(
        id=locale.id,
        key=locale.key,
        value=locale.value,
        language=locale.language,
        namespace=locale.namespace,
        is_active=locale.is_active,
        created_at=locale.created_at,
        updated_at=locale.updated_at
    )


@strawberry.type
class LocaleQuery:
    @strawberry.field
    def locales(
        self,
        filter: Optional[LocaleFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LocaleType]:
        """Get list of locales with optional filtering"""
        db = next(get_db())
        query = db.query(Locale)
        
        if filter:
            if filter.language:
                query = query.filter(Locale.language == filter.language)
            if filter.namespace:
                query = query.filter(Locale.namespace == filter.namespace)
            if filter.is_active is not None:
                query = query.filter(Locale.is_active == filter.is_active)
        
        locales = query.offset(skip).limit(limit).all()
        return [locale_model_to_type(locale) for locale in locales]

    @strawberry.field
    def locale(
        self,
        id: int
    ) -> Optional[LocaleType]:
        """Get locale by ID"""
        db = next(get_db())
        locale = db.query(Locale).filter(Locale.id == id).first()
        if not locale:
            return None
        return locale_model_to_type(locale)

    @strawberry.field
    def export_locales(
        self,
        language: str,
        namespace: Optional[str] = None
    ) -> str:
        """Export locales in JSON format"""
        db = next(get_db())
        query = db.query(Locale).filter(
            and_(Locale.language == language, Locale.is_active == True)
        )
        
        if namespace:
            query = query.filter(Locale.namespace == namespace)
        
        locales = query.all()
        
        result = {}
        for locale in locales:
            if locale.namespace not in result:
                result[locale.namespace] = {}
            result[locale.namespace][locale.key] = locale.value
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)


@strawberry.type
class LocaleMutation:
    @strawberry.mutation
    def create_locale(
        self,
        input: LocaleCreateInput
    ) -> LocaleType:
        """Create new locale"""
        db = next(get_db())
        # Check if combination of key + language + namespace already exists
        existing = db.query(Locale).filter(
            and_(
                Locale.key == input.key,
                Locale.language == input.language,
                Locale.namespace == input.namespace
            )
        ).first()
        
        if existing:
            raise ValueError("Locale with such key, language and namespace already exists")
        
        db_locale = Locale(
            key=input.key,
            value=input.value,
            language=input.language,
            namespace=input.namespace,
            is_active=input.is_active
        )
        db.add(db_locale)
        db.commit()
        db.refresh(db_locale)
        return locale_model_to_type(db_locale)

    @strawberry.mutation
    def update_locale(
        self,
        id: int,
        input: LocaleUpdateInput
    ) -> Optional[LocaleType]:
        """Update locale"""
        db = next(get_db())
        db_locale = db.query(Locale).filter(Locale.id == id).first()
        if not db_locale:
            return None
        
        # Update only provided fields
        if input.key is not None:
            db_locale.key = input.key
        if input.value is not None:
            db_locale.value = input.value
        if input.language is not None:
            db_locale.language = input.language
        if input.namespace is not None:
            db_locale.namespace = input.namespace
        if input.is_active is not None:
            db_locale.is_active = input.is_active
        
        db.commit()
        db.refresh(db_locale)
        return locale_model_to_type(db_locale)

    @strawberry.mutation
    def delete_locale(
        self,
        id: int
    ) -> DeleteResponse:
        """Delete locale"""
        db = next(get_db())
        db_locale = db.query(Locale).filter(Locale.id == id).first()
        if not db_locale:
            return DeleteResponse(success=False, message="Locale not found")
        
        db.delete(db_locale)
        db.commit()
        return DeleteResponse(success=True, message="Locale successfully deleted")
