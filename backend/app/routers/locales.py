from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.locale import Locale
from app.schemas.locale import LocaleCreate, LocaleUpdate, LocaleResponse

router = APIRouter()


@router.get("/", response_model=List[LocaleResponse])
async def get_locales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    language: Optional[str] = None,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of locales with filtering"""
    query = db.query(Locale)
    
    if language:
        query = query.filter(Locale.language == language)
    if namespace:
        query = query.filter(Locale.namespace == namespace)
    
    locales = query.offset(skip).limit(limit).all()
    return locales


@router.get("/{locale_id}", response_model=LocaleResponse)
async def get_locale(locale_id: int, db: Session = Depends(get_db)):
    """Get locale by ID"""
    locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not locale:
        raise HTTPException(status_code=404, detail="Locale not found")
    return locale


@router.post("/", response_model=LocaleResponse)
async def create_locale(locale: LocaleCreate, db: Session = Depends(get_db)):
    """Create new locale"""
    # Check if combination of key + language + namespace already exists
    existing = db.query(Locale).filter(
        Locale.key == locale.key,
        Locale.language == locale.language,
        Locale.namespace == locale.namespace
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Locale with such key, language and namespace already exists"
        )
    
    db_locale = Locale(**locale.dict())
    db.add(db_locale)
    db.commit()
    db.refresh(db_locale)
    return db_locale


@router.put("/{locale_id}", response_model=LocaleResponse)
async def update_locale(
    locale_id: int, 
    locale_update: LocaleUpdate, 
    db: Session = Depends(get_db)
):
    """Update locale"""
    db_locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not db_locale:
        raise HTTPException(status_code=404, detail="Locale not found")
    
    update_data = locale_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_locale, field, value)
    
    db.commit()
    db.refresh(db_locale)
    return db_locale


@router.delete("/{locale_id}")
async def delete_locale(locale_id: int, db: Session = Depends(get_db)):
    """Delete locale"""
    db_locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not db_locale:
        raise HTTPException(status_code=404, detail="Locale not found")
    
    db.delete(db_locale)
    db.commit()
    return {"message": "Locale successfully deleted"}


@router.get("/export/{language}")
async def export_locales(
    language: str,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export locales in JSON format"""
    query = db.query(Locale).filter(Locale.language == language, Locale.is_active)
    
    if namespace:
        query = query.filter(Locale.namespace == namespace)
    
    locales = query.all()
    
    result = {}
    for locale in locales:
        if locale.namespace not in result:
            result[locale.namespace] = {}
        result[locale.namespace][locale.key] = locale.value
    
    return result
