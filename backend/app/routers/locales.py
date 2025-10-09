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
    """Получить список локализаций с фильтрацией"""
    query = db.query(Locale)
    
    if language:
        query = query.filter(Locale.language == language)
    if namespace:
        query = query.filter(Locale.namespace == namespace)
    
    locales = query.offset(skip).limit(limit).all()
    return locales


@router.get("/{locale_id}", response_model=LocaleResponse)
async def get_locale(locale_id: int, db: Session = Depends(get_db)):
    """Получить локализацию по ID"""
    locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not locale:
        raise HTTPException(status_code=404, detail="Локализация не найдена")
    return locale


@router.post("/", response_model=LocaleResponse)
async def create_locale(locale: LocaleCreate, db: Session = Depends(get_db)):
    """Создать новую локализацию"""
    # Проверяем, не существует ли уже такая комбинация key + language + namespace
    existing = db.query(Locale).filter(
        Locale.key == locale.key,
        Locale.language == locale.language,
        Locale.namespace == locale.namespace
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Локализация с таким ключом, языком и пространством имен уже существует"
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
    """Обновить локализацию"""
    db_locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not db_locale:
        raise HTTPException(status_code=404, detail="Локализация не найдена")
    
    update_data = locale_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_locale, field, value)
    
    db.commit()
    db.refresh(db_locale)
    return db_locale


@router.delete("/{locale_id}")
async def delete_locale(locale_id: int, db: Session = Depends(get_db)):
    """Удалить локализацию"""
    db_locale = db.query(Locale).filter(Locale.id == locale_id).first()
    if not db_locale:
        raise HTTPException(status_code=404, detail="Локализация не найдена")
    
    db.delete(db_locale)
    db.commit()
    return {"message": "Локализация успешно удалена"}


@router.get("/export/{language}")
async def export_locales(
    language: str,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Экспортировать локализации в формате JSON"""
    query = db.query(Locale).filter(Locale.language == language, Locale.is_active == True)
    
    if namespace:
        query = query.filter(Locale.namespace == namespace)
    
    locales = query.all()
    
    result = {}
    for locale in locales:
        if locale.namespace not in result:
            result[locale.namespace] = {}
        result[locale.namespace][locale.key] = locale.value
    
    return result
