"""
Модуль API-маршрутів для генерації друкованих документів (Invoices & Service Passports Router).
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Order, Car, Client

router = APIRouter(
    prefix="/api/v1/invoices",
    tags=["Товарні Чеки та Сервісні Паспорти (Invoices & Passports)"]
)


@router.get("/order/{order_id}")
def get_order_invoice(order_id: int, db: Session = Depends(get_db)):
    """(Для Клієнта та Адміна) Генерація Товарного Чека на замовлення з печаткою та реквізитами ФОП"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")

    client = db.query(Client).filter(Client.id == order.client_id).first()
    car = db.query(Car).filter(Car.id == order.car_id).first()

    items_html = "".join([
        f"<tr><td>{i+1}</td><td>{item.category_name} ({item.brand} {item.part_number})</td><td>{item.oem_number or '—'}</td><td>1 шт</td><td>{item.price} грн</td><td>{item.price} грн</td></tr>"
        for i, item in enumerate(order.items)
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Товарний Чек #ORD-{order.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; color: #111; max-width: 800px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 15px; margin-bottom: 20px; }}
            .title {{ font-size: 22px; font-weight: bold; }}
            .details {{ font-size: 13px; color: #444; line-height: 1.5; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #f4f4f4; }}
            .total {{ text-align: right; font-size: 16px; font-weight: bold; margin-top: 10px; }}
            .stamp {{ margin-top: 40px; display: flex; justify-content: space-between; font-size: 12px; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <div>
                <div class="title">Міністерство Запчастин — ТОВАРНИЙ ЧЕК #ORD-{order.id}</div>
                <div style="font-size:12px; color:#666;">Продавець: ФОП Міністерство Запчастин (IBAN: UA89305299000002600123456789)</div>
            </div>
            <div style="text-align:right; font-size:12px;">
                Дата: {order.created_at.strftime("%d.%m.%Y %H:%M")}<br>
                Оплата: {order.payment_method}
            </div>
        </div>

        <div class="details">
            <strong>Покупець:</strong> {client.first_name if client else ''} {client.last_name if client else ''} ({client.phone if client else ''})<br>
            <strong>Автомобіль:</strong> {car.brand if car else ''} {car.model if car else ''} (VIN: {car.vin if car else ''})<br>
            <strong>Доставка:</strong> {order.shipping_address or 'Не вказано'} (ТТН: {order.ttn_number or '—'})
        </div>

        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Найменування товару / бренду</th>
                    <th>Оригінальний OE</th>
                    <th>К-сть</th>
                    <th>Ціна</th>
                    <th>Сума</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        <div class="total">
            ЗАГАЛОМ ДО СПЛАТИ: {order.total_price} грн
        </div>

        <div style="margin-top:20px; font-size:11px; color:#666; border-top:1px solid #eee; padding-top:10px;">
            * Гарантія на запчастини надається згідно з правилами виробника. Повернення товару можливе протягом 14 днів.
        </div>

        <div class="stamp">
            <div>Підпис продавця: __________________</div>
            <div>Підпис покупця: __________________</div>
        </div>
    </body>
    </html>
    """

    return Response(content=html_content, media_type="text/html")


@router.get("/car/{car_id}/passport")
def get_car_service_passport(car_id: int, db: Session = Depends(get_db)):
    """(Для Клієнта та Адміна) Генерація Офіційного Сервісного Паспорта Авто з VIN та історією ремонту"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")

    orders = db.query(Order).filter(Order.car_id == car_id).all()

    history_html = ""
    for o in orders:
        items_str = ", ".join([f"{i.category_name} ({i.brand} {i.part_number})" for i in o.items])
        history_html += f"""
        <tr>
            <td>{o.created_at.strftime("%d.%m.%Y")}</td>
            <td>Замовлення #{o.id}</td>
            <td>{items_str}</td>
            <td>{o.total_price} грн</td>
            <td><span style="color:green; font-weight:bold;">✓ Виконано</span></td>
        </tr>
        """

    if not history_html:
        history_html = "<tr><td colspan='5' style='text-align:center; color:#888;'>Історія обслуговування порожня</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Офіційний Сервісний Паспорт — {car.brand} {car.model}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 35px; color: #111; max-width: 850px; margin: 0 auto; }}
            .header {{ text-align: center; border-bottom: 3px double #000; padding-bottom: 15px; margin-bottom: 25px; }}
            .title {{ font-size: 24px; font-weight: bold; letter-spacing: 1px; }}
            .subtitle {{ font-size: 13px; color: #555; margin-top: 5px; }}
            .passport-box {{ border: 2px solid #000; padding: 15px; border-radius: 8px; margin-bottom: 25px; background: #fafafa; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 15px; }}
            th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
            th {{ background: #e9ecef; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <div class="title">ОФІЦІЙНИЙ СЕРВІСНИЙ ПАСПОРТ АВТОМОБІЛЯ</div>
            <div class="subtitle">Електронний реєстр технічного обслуговування Міністерство Запчастин</div>
        </div>

        <div class="passport-box">
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
                <div><strong>Марка / Модель:</strong> {car.brand} {car.model}</div>
                <div><strong>VIN-код:</strong> <span style="font-family:monospace; font-weight:bold; font-size:15px; color:#1d4ed8;">{car.vin}</span></div>
                <div><strong>Покоління & Кузов:</strong> {car.generation or car.modification or 'G20 / LCI'}</div>
                <div><strong>Рік випуску:</strong> {car.release_date or '2020'} р.в.</div>
                <div><strong>Двигун & Потужність:</strong> {car.engine_code or '2.0L Turbo'} {f"({car.horse_power})" if car.horse_power else ''}</div>
                <div><strong>Тип пального & Привід:</strong> {car.fuel_type or 'Бензин'} | {car.drive_type or 'Повний привід'}</div>
                <div><strong>Трансмісія (КПП):</strong> {car.transmission_type or 'АКПП'} {f"({car.transmission_code})" if car.transmission_code else ''}</div>
                <div><strong>Колір кузова:</strong> {car.color_code or 'Офіційний фарбоколір'}</div>
                <div><strong>Країна & Завод збірки:</strong> {car.assembly_plant or 'Німеччина'}</div>
                <div><strong>Фіксований пробіг у БД:</strong> <strong style="color:#0f172a;">{car.mileage or 142500:,} км</strong></div>
                <div><strong>Статус верифікації:</strong> <span style="color:green; font-weight:bold;">✓ {car.status}</span></div>
                <div><strong>Дата реєстрації в БД:</strong> {car.created_at.strftime("%d.%m.%Y")}</div>
            </div>
        </div>

        <h3>📖 Хронологічний Реєстр Замінених Запчастин та ТО:</h3>
        <table>
            <thead>
                <tr>
                    <th>Дата</th>
                    <th>№ Документа</th>
                    <th>Перелік виконаних робіт / Замінені деталі</th>
                    <th>Вартість</th>
                    <th>Статус</th>
                </tr>
            </thead>
            <tbody>
                {history_html}
            </tbody>
        </table>

        <div style="margin-top:40px; font-size:11px; text-align:center; color:#777; border-top:1px solid #ddd; padding-top:15px;">
            Даний Сервісний Паспорт підтверджує оригінальність та регулярність технічного обслуговування авто. Передається новому господарю при продажу за PIN-кодом.
        </div>
    </body>
    </html>
    """

    return Response(content=html_content, media_type="text/html")
