"""
Модуль API-маршрутів для довідника міст та відділень Нової Пошти (Nova Poshta Router).
"""

from typing import List, Optional
from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/api/v1/novaposhta",
    tags=["Довідник Нової Пошти (Nova Poshta Cities & Branches)"]
)

# Базовий довідник міст України
CITIES_DATA = [
    {"id": "dnipro", "name": "м. Дніпро"},
    {"id": "kyiv", "name": "м. Київ"},
    {"id": "kharkiv", "name": "м. Харків"},
    {"id": "odesa", "name": "м. Одеса"},
    {"id": "lviv", "name": "м. Львів"},
    {"id": "zaporizhzhia", "name": "м. Запоріжжя"},
    {"id": "kryvyi_rih", "name": "м. Кривий Ріг"},
    {"id": "mykolaiv", "name": "м. Миколаїв"},
    {"id": "vinnytsia", "name": "м. Вінниця"},
    {"id": "poltava", "name": "м. Полтава"}
]

# Відділення НП по містах
BRANCHES_DATA = {
    "dnipro": [
        "Відділення №1 (вул. Маршала Малиновського, 114)",
        "Відділення №12 (просп. Дмитра Яворницького, 88)",
        "Відділення №25 (просп. Богдана Хмельницького, 31D)",
        "Поштомат №10542 (просп. Гагаріна, 40)"
    ],
    "kyiv": [
        "Відділення №1 (вул. Пирогівський шлях, 135)",
        "Відділення №5 (вул. Федорова, 32)",
        "Відділення №11 (вул. Верхній Вал, 24)",
        "Відділення №88 (вул. Хрещатик, 15)"
    ],
    "kharkiv": [
        "Відділення №1 (вул. Польова, 67)",
        "Відділення №10 (вул. Сумська, 47)",
        "Відділення №34 (просп. Науки, 25)"
    ],
    "lviv": [
        "Відділення №1 (вул. Городоцька, 355)",
        "Відділення №8 (вул. Героїв УПА, 76)",
        "Відділення №15 (вул. Дорошенка, 22)"
    ]
}

@router.get("/cities")
def get_cities(query: Optional[str] = Query(None, description="Пошук міста українською")):
    """Отримання довідника міст України для доставки"""
    if not query:
        return CITIES_DATA
    q = query.strip().lower()
    return [c for c in CITIES_DATA if q in c["name"].lower()]

@router.get("/branches")
def get_branches(city_id: str = Query("dnipro", description="ID міста")):
    """Отримання списку відділень Нової Пошти для вибраного міста"""
    branches = BRANCHES_DATA.get(city_id, [
        "Відділення №1 (Головне)",
        "Відділення №2 (Центральне)",
        "Відділення №3"
    ])
    return {"city_id": city_id, "branches": branches}
