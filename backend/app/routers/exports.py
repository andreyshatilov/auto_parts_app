"""
Модуль API-маршрутів для експорту даних у форматах CSV/Excel (Exports Router).
"""

import csv
import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, Order

router = APIRouter(
    prefix="/api/v1/exports",
    tags=["Експорт Звітів у CSV (Data Exporters)"]
)


@router.get("/clients/csv")
def export_clients_csv(db: Session = Depends(get_db)):
    """(Для Адміна) Завантаження реєстру клієнтів у файлі CSV"""
    clients = db.query(Client).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Ім'я", "Прізвище", "Телефон", "Адреса Нової Пошти", "Кількість авто", "Замовлень"])

    for c in clients:
        writer.writerow([c.id, c.first_name, c.last_name, c.phone, c.shipping_address or "", len(c.cars), c.completed_orders_count])

    content = output.getvalue().encode('utf-8-sig') # UTF-8 с BOM для відкриття в Excel
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients_export.csv"}
    )


@router.get("/orders/csv")
def export_orders_csv(db: Session = Depends(get_db)):
    """(Для Адміна) Завантаження реєстру замовлень та прибутку у файлі CSV"""
    orders = db.query(Order).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID Замовлення", "Клієнт ID", "Статус", "Спосіб оплати", "Виторг грн", "Закупівля грн", "Прибуток грн", "ТТН НП", "Дата"])

    for o in orders:
        cost = float(o.purchase_cost or 0)
        total = float(o.total_price)
        profit = total - cost
        writer.writerow([o.id, o.client_id, o.status, o.payment_method, total, cost, profit, o.ttn_number or "", o.created_at.strftime("%Y-%m-%d %H:%M")])

    content = output.getvalue().encode('utf-8-sig')
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )
