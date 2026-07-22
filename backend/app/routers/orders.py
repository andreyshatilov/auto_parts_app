"""
Модуль API-маршрутов для управления заказами клиентов (Orders Router).

Реализует оформление заказа, сборку товаров с прикреплением фото,
генерацию ссылок отслеживания Новой Почты и повтор заказов из истории.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import re

from app.database import get_db
from app.models import Client, Car, Order, OrderItem, OrderRequest
from app.schemas import OrderCreate, OrderStatusUpdate, OrderResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Заказы и Трекинг НП (Orders & Shipping)"]
)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Клиент) Оформление заказа на основании выбранных аналогов из сметы.
    """
    # 1. Проверяем авто в гараже клиента
    car = db.query(Car).filter(Car.id == data.car_id, Car.client_id == current_client.id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден в вашем гараже"
        )

    # 2. Считаем общую стоимость выбранных позиций
    total = sum(item.price for item in data.items)

    shipping_addr = data.shipping_address or current_client.shipping_address
    if data.shipping_address:
        current_client.shipping_address = data.shipping_address

    new_order = Order(
        client_id=current_client.id,
        car_id=car.id,
        proposal_id=data.proposal_id,
        status="sent_to_preparation",
        payment_method=data.payment_method or "cash_on_delivery",
        total_price=total,
        shipping_address=shipping_addr
    )

    db.add(new_order)
    db.flush()

    # 4. Добавляем выбранные позиций
    for item_in in data.items:
        new_item = OrderItem(
            order_id=new_order.id,
            category_name=item_in.category_name,
            oem_number=item_in.oem_number,
            brand=item_in.brand,
            part_number=item_in.part_number,
            price=item_in.price,
            delivery_term=item_in.delivery_term or "1-2 дня"
        )
        db.add(new_item)

    # Увеличиваем счетчик заказов у клиента
    current_client.completed_orders_count += 1

    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Клиент) Просмотр всей истории моих заказов, фото собранного товара и ТТН Новой Почты.
    """
    orders = db.query(Order).filter(
        Order.client_id == current_client.id
    ).order_by(Order.created_at.desc()).all()
    return orders


@router.get("/", response_model=List[OrderResponse])
def get_all_orders(
    status_filter: Optional[str] = Query(None, description="sent_to_preparation / assembling / ready_for_shipping / shipped / delivered"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """(Для Админа) Просмотр всех заказов в работе"""
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    (Для Админа) Обновление статуса заказа, добавление фото сборки и ТТН Новой Почты.
    
    При вводе номера ТТН (например: 20450897123456) автоматически генерируется ссылка отслеживания НП!
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )

    if data.status:
        order.status = data.status

    if data.assembly_photo_url:
        order.assembly_photo_url = data.assembly_photo_url

    if data.purchase_cost is not None:
        order.purchase_cost = data.purchase_cost

    if data.ttn_number:
        clean_ttn = re.sub(r"\D", "", data.ttn_number.strip())
        order.ttn_number = clean_ttn
        # Автоматическая генерация ссылки отслеживания сайта Новой Почты
        order.ttn_tracking_url = f"https://novaposhta.ua/tracking/?cargo_number={clean_ttn}"
        if not data.status:
            order.status = "shipped"

    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/repeat")
def repeat_order(
    order_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Клиент) Повтор заказа из истории.
    
    Формирует новый запрос к эксперту на основании прошлых деталей для актуализации цен.
    """
    old_order = db.query(Order).filter(Order.id == order_id, Order.client_id == current_client.id).first()
    if not old_order:
        raise HTTPException(status_code=404, detail="Заказ не найден в вашей истории")

    # Собираем список позиций текстом
    items_str = ", ".join([f"{item.category_name} ({item.brand} {item.part_number})" for item in old_order.items])
    repeat_text = f"Повтор заказа #{old_order.id}: {items_str}"

    new_request = OrderRequest(
        client_id=current_client.id,
        car_id=old_order.car_id,
        client_message=repeat_text,
        status="sent"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "Запрос на повтор заказа успешно отправлен эксперту!",
        "new_request_id": new_request.id
    }
