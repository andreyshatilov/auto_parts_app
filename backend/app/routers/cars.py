"""
Модуль API-маршрутов для управления автомобилями (Car Router).

Предоставляет эндпоинты для добавления, поиска, обновления и удаления авто из базы.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Car
from app.schemas import CarCreate, CarResponse, CarUpdate

router = APIRouter(
    prefix="/api/v1/cars",
    tags=["Автомобили (Cars)"]
)


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(car_in: CarCreate, db: Session = Depends(get_db)):
    """
    Добавление нового автомобиля в базу данных.
    
    - Проверяет, нет ли уже авто с таким VIN-кодом в базе.
    - Вносит полную техническую карту автомобиля.
    """
    # 1. Проверяем, существует ли уже авто с таким VIN
    existing_car = db.query(Car).filter(Car.vin == car_in.vin).first()
    if existing_car:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Автомобиль с VIN '{car_in.vin}' уже существует в базе данных (ID: {existing_car.id})"
        )

    # 2. Создаем объект модели SQLAlchemy из входных данных
    new_car = Car(**car_in.model_dump())

    # 3. Сохраняем в базу данных
    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car


@router.get("/", response_model=List[CarResponse])
def get_cars(
    search: Optional[str] = Query(None, description="Поиск по VIN, марке, модели или коду двигателя"),
    skip: int = Query(0, ge=0, description="Смещение списка (пагинация)"),
    limit: int = Query(100, ge=1, le=500, description="Количество записей"),
    db: Session = Depends(get_db)
):
    """
    Получение списка автомобилей из базы данных.
    
    Поддерживает поиск `search`: ищет совпадение по VIN, Марке, Модели или Коду Двигателя.
    """
    query = db.query(Car)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Car.vin.ilike(search_pattern),
                Car.brand.ilike(search_pattern),
                Car.model.ilike(search_pattern),
                Car.engine_code.ilike(search_pattern),
                Car.modification.ilike(search_pattern)
            )
        )

    # Сортировка: сначала самые новые внесенные автомобили
    cars = query.order_by(Car.created_at.desc()).offset(skip).limit(limit).all()
    return cars


@router.get("/{car_id}", response_model=CarResponse)
def get_car_by_id(car_id: int, db: Session = Depends(get_db)):
    """Получение детальной информации об авто по его ID"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Автомобиль с ID {car_id} не найден"
        )
    return car


@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db)):
    """Обновление характеристик автомобиля"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Автомобиль с ID {car_id} не найден"
        )

    update_data = car_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    """Удаление автомобиля из базы данных"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Автомобиль с ID {car_id} не найден"
        )

    db.delete(car)
    db.commit()
    return None
