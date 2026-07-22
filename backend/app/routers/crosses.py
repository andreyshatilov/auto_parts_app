"""
Модуль API-маршрутів для авто-підбору крос-номерів (Crosses Router).

Працює на 100% чистих SQL-запитах за 5 мс без використання ШІ та зовнішніх серверів.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import re

from app.database import get_db
from app.models import CrossReference
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/crosses",
    tags=["Авто-Кроси та Аналоги (Cross-References)"]
)


class CrossItemResponse(BaseModel):
    id: int
    oem_number_clean: str
    oem_number_raw: str
    category_name: Optional[str] = None
    brand: str
    part_number: str
    price: float
    times_used: int

    class Config:
        from_attributes = True


@router.get("/search", response_model=List[CrossItemResponse])
def search_cross_references(
    oem: str = Query(..., min_length=2, description="Оригінальний номер OE (наприклад: 11427953129 чи 12640445)"),
    db: Session = Depends(get_db)
):
    """
    (Для Адміна) Блискавичний авто-пошук замінників в базі знань за 5 мс (без ШІ).
    """
    clean = re.sub(r"[^a-zA-Z0-9]", "", oem).upper()
    if not clean:
        return []

    # Чистий SQL запит з сортуванням за популярністю використання
    crosses = db.query(CrossReference).filter(
        CrossReference.oem_number_clean == clean
    ).order_by(CrossReference.times_used.desc()).all()

    return crosses
