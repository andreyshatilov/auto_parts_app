"""
Модуль API-маршрутов для запросов на подбор запчастей (Requests Router).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Car, OrderRequest
from app.schemas import OrderRequestCreate, OrderRequestResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/requests",
    tags=["Запросы на подбор (Order Requests)"]
)


@router.post("/", response_model=OrderRequestResponse, status_code=status.HTTP_201_CREATED)
def create_order_request(
    data: OrderRequestCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Клиент) Подача текстового запроса на подбор запчастей для авто из своего гаража.
    """
    # 1. Проверяем, что авто принадлежит клиенту
    car = db.query(Car).filter(Car.id == data.car_id, Car.client_id == current_client.id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Выбранный автомобиль не найден в вашем гараже"
        )

    # 2. Создаем запрос в статусе "sent"
    new_request = OrderRequest(
        client_id=current_client.id,
        car_id=car.id,
        client_message=data.client_message.strip(),
        photo_url=data.photo_url,
        status="sent"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/my", response_model=List[OrderRequestResponse])
def get_my_requests(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """(Клиент) Список всех моих прошлых запросов и ответов по ним"""
    requests = db.query(OrderRequest).filter(
        OrderRequest.client_id == current_client.id
    ).order_by(OrderRequest.created_at.desc()).all()
    return requests


@router.get("/", response_model=List[OrderRequestResponse])
def get_all_requests(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу: sent / in_progress / completed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """(Для Админа) Просмотр очереди входящих запросов клиентов"""
    query = db.query(OrderRequest)
    if status_filter:
        query = query.filter(OrderRequest.status == status_filter)

    requests = query.order_by(OrderRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.get("/{request_id}", response_model=OrderRequestResponse)
def get_request_by_id(request_id: int, db: Session = Depends(get_db)):
    """Получение информации по конкретному запросу"""
    req = db.query(OrderRequest).filter(OrderRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    return req
