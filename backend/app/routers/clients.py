"""
Модуль API-маршрутов для работы с клиентами и их "Гаражом" (Clients Router).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Client, Car
from app.schemas import ClientResponse, ClientUpdate, CarCreate, CarResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/clients",
    tags=["Клиенты и Гараж (Clients & Garage)"]
)


# --- МАРШРУТЫ АВТОРИЗОВАННОГО КЛИЕНТА ---

@router.get("/me/cars", response_model=List[CarResponse])
def get_my_garage(current_client: Client = Depends(get_current_client)):
    """Получить список автомобилей из своего личного 'Гаража'"""
    return current_client.cars


@router.post("/me/cars", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def add_car_to_my_garage(
    car_in: CarCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Добавление нового автомобиля в свой личный "Гараж".
    
    Автомобиль автоматически привязывается к текущему вошедшему клиенту (`client_id`).
    """
    # 1. Проверяем дубликаты по VIN
    existing = db.query(Car).filter(Car.vin == car_in.vin).first()
    if existing:
        if existing.client_id == current_client.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Этот автомобиль с VIN '{car_in.vin}' уже находится в вашем гараже!"
            )
        else:
            # При перепродаже машины: обновляем владельца в базе
            existing.client_id = current_client.id
            db.commit()
            db.refresh(existing)
            return existing

    # 2. Создаем авто с привязкой к ID клиента
    car_data = car_in.model_dump()
    car_data["client_id"] = current_client.id

    new_car = Car(**car_data)
    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car


@router.delete("/me/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_car(
    car_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Повне видалення авто з гаража клієнта та бази даних"""
    car = db.query(Car).filter(Car.id == car_id, Car.client_id == current_client.id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Автомобіль з ID {car_id} не знайдено у вашому гаражі"
        )

    # Видаляємо авто з бази даних повністю
    db.delete(car)
    db.commit()
    return None


@router.put("/me", response_model=ClientResponse)
def update_my_profile(
    data: ClientUpdate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Обновление личных данных и адреса доставки Новой Почты"""
    update_dict = data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(current_client, key, value)

    db.commit()
    db.refresh(current_client)
    return current_client


# --- МАРШРУТЫ АДМИНИСТРАТОРА ---

@router.get("/", response_model=List[ClientResponse])
def get_all_clients(
    search: Optional[str] = Query(None, description="Поиск по имени, фамилии или телефону"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """(Для Админа) Просмотр реестра всех зарегистрированных клиентов"""
    query = db.query(Client)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Client.first_name.ilike(search_pattern),
                Client.last_name.ilike(search_pattern),
                Client.phone.ilike(search_pattern)
            )
        )

    clients = query.order_by(Client.registered_at.desc()).offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client_by_id(client_id: int, db: Session = Depends(get_db)):
    """(Для Админа) Просмотр карточки конкретного клиента и всех авто в его гараже"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    return client
