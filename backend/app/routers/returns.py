"""
Модуль API-маршрутів для управління поверненнями товарів (Returns Router).

Реалізує правила повернення:
- до 10 днів: авто-повернення в 1 клік,
- 10-14 днів: через форму обґрунтування,
- понад 14 днів: гарантійний випадок або помилковий підбір експерта.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Order, OrderReturn
from app.schemas import OrderReturnCreate, OrderReturnResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/returns",
    tags=["Повернення товарів (Order Returns)"]
)


@router.post("/", response_model=OrderReturnResponse, status_code=status.HTTP_201_CREATED)
def create_order_return(
    data: OrderReturnCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    (Клієнт) Оформлення заявки на повернення товару.
    """
    # 1. Перевіряємо, що замовлення належить клієнту
    order = db.query(Order).filter(Order.id == data.order_id, Order.client_id == current_client.id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Замовлення не знайдено у вашій історії"
        )

    # 2. Вираховуємо кількість днів з моменту оформлення замовлення
    delta_days = (datetime.utcnow() - order.created_at).days

    if delta_days <= 10:
        ret_type = "auto_10_days"
    elif delta_days <= 14:
        ret_type = "form_10_14_days"
    else:
        ret_type = "guarantee_over_14"

    # 3. Створюємо заявку на повернення
    new_return = OrderReturn(
        order_id=order.id,
        client_id=current_client.id,
        reason=data.reason.strip(),
        return_type=ret_type,
        status="requested"
    )

    db.add(new_return)
    db.commit()
    db.refresh(new_return)

    return new_return


@router.get("/my", response_model=List[OrderReturnResponse])
def get_my_returns(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """(Клієнт) Перегляд моїх заявок на повернення"""
    returns = db.query(OrderReturn).filter(
        OrderReturn.client_id == current_client.id
    ).order_by(OrderReturn.created_at.desc()).all()
    return returns


@router.get("/", response_model=List[OrderReturnResponse])
def get_all_returns(
    status_filter: Optional[str] = Query(None, description="requested / approved / rejected / completed"),
    db: Session = Depends(get_db)
):
    """(Для Адміна) Реєстр всіх заявок на повернення"""
    query = db.query(OrderReturn)
    if status_filter:
        query = query.filter(OrderReturn.status == status_filter)

    return query.order_by(OrderReturn.created_at.desc()).all()


@router.put("/{return_id}/status", response_model=OrderReturnResponse)
def update_return_status(
    return_id: int,
    status_val: str = Query(..., description="approved / rejected / completed"),
    db: Session = Depends(get_db)
):
    """(Для Адміна) Зміна статусу заявки на повернення"""
    ret = db.query(OrderReturn).filter(OrderReturn.id == return_id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Заявка на повернення не знайдена")

    ret.status = status_val
    db.commit()
    db.refresh(ret)
    return ret
