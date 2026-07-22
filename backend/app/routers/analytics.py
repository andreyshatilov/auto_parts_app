"""
Модуль API-маршрутів для фінансової аналітики P&L (Analytics Router).

Розраховує виторг, закупівельні витрати, чистий прибуток (маржу), середній чек та топ клієнтів.
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Order, Client

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Фінансова Аналітика P&L (Financial Analytics)"]
)


@router.get("/summary")
def get_financial_summary(
    days: Optional[int] = Query(30, description="Період аналітики у днях (за замовчуванням 30)"),
    db: Session = Depends(get_db)
):
    """
    (Для Керівника/Адміна) Фінансовий звіт P&L: Виторг, Закупівля, Прибуток та Маржинальність.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    orders = db.query(Order).filter(Order.created_at >= start_date).all()

    total_revenue = sum(float(o.total_price) for o in orders)
    total_cost = sum(float(o.purchase_cost or 0) for o in orders)
    net_profit = total_revenue - total_cost
    margin_percent = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    avg_order_val = (total_revenue / len(orders)) if len(orders) > 0 else 0.0

    # Топ 5 клієнтів за сумою замовлень
    top_clients_query = db.query(
        Client.first_name,
        Client.last_name,
        Client.phone,
        func.sum(Order.total_price).label("total_spent"),
        func.count(Order.id).label("orders_count")
    ).join(Order, Client.id == Order.client_id).group_by(Client.id).order_by(func.sum(Order.total_price).desc()).limit(5).all()

    top_clients = [
        {
            "name": f"{tc[0]} {tc[1]}",
            "phone": tc[2],
            "total_spent": float(tc[3]),
            "orders_count": tc[4]
        }
        for tc in top_clients_query
    ]

    return {
        "period_days": days,
        "total_orders": len(orders),
        "total_revenue_uah": round(total_revenue, 2),
        "total_purchase_cost_uah": round(total_cost, 2),
        "net_profit_uah": round(net_profit, 2),
        "margin_percent": round(margin_percent, 1),
        "avg_order_value_uah": round(avg_order_val, 2),
        "top_clients": top_clients
    }
