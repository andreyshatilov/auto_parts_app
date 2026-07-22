"""
Модуль API-маршрутів для способів оплати та реквізитів ФОП (Payments Router).
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Оплата та Реквізити (Payments)"]
)


@router.get("/methods")
def get_payment_methods():
    """Повертає доступні способи оплати та реквізити ФОП в Україні"""
    return {
        "methods": [
            {
                "id": "cash_on_delivery",
                "name": "🚚 Накладений платіж Нової Пошти",
                "description": "Оплата готівкою або карткою при отриманні у відділенні Нової Почти"
            },
            {
                "id": "fop_prepayment",
                "name": "💳 Передплата на розрахунковий рахунок ФОП",
                "description": "Оплата за реквізитами IBAN у застосунку Приват24 / Monobank",
                "requisites": {
                    "fop_name": "ФОП Петренко Іван Олександрович",
                    "code_edrpou": "3284910293",
                    "iban": "UA82305299000002600123456789",
                    "bank": "АТ КБ 'ПРИВАТБАНК'"
                }
            },
            {
                "id": "partial_prepayment",
                "name": "⚖️ Часткова передплата (аванс 20%)",
                "description": "Обов'язково для рідкісних запчастин на замовлення з Європи/США"
            }
        ]
    }
