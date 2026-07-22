"""
Тестовый скрипт проверки Фазы 4:
- Оформление заказа клиентом из сметы
- Фотофиксация сборки товара
- Прикрепление ТТН Новой Почты и генерация ссылки отслеживания
- Повтор заказа из истории
"""

from app.database import engine, Base, SessionLocal
from app.schemas import (
    ClientRegister, CarCreate, OrderRequestCreate,
    ProposalCreate, ProposalItemCreate, ProposalAlternativeCreate,
    OrderCreate, OrderItemCreate, OrderStatusUpdate
)
from app.routers.auth import register_client
from app.routers.clients import add_car_to_my_garage
from app.routers.requests import create_order_request
from app.routers.proposals import create_proposal
from app.routers.orders import create_order, update_order_status, get_my_orders, repeat_order

def test_phase4_complete():
    print("1. Пересоздание схемы БД для Фазы 4...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("2. Регистрация клиента и добавление авто BMW 523i...")
        res = register_client(ClientRegister(
            first_name="Иван", last_name="Петров", phone="+380931234567", shipping_address="г. Днепр, НП №12"
        ), db)
        client = res["client"]

        car = add_car_to_my_garage(CarCreate(
            vin="WBAFP31010C502209", brand="BMW", model="523i", modification="F10", engine_code="N52N"
        ), current_client=client, db=db)

        print("3. Подача запроса и составление сметы...")
        req = create_order_request(OrderRequestCreate(car_id=car.id, client_message="Масляный фильтр"), current_client=client, db=db)
        prop = create_proposal(ProposalCreate(
            request_id=req.id,
            items=[
                ProposalItemCreate(
                    category_name="Масляный фильтр", oem_number="11427953129",
                    alternatives=[ProposalAlternativeCreate(brand="Knecht", part_number="OX387D", price=460.0)]
                )
            ]
        ), db=db)

        print("4. Оформление заказа клиентом...")
        order = create_order(OrderCreate(
            car_id=car.id, proposal_id=prop.id,
            items=[OrderItemCreate(category_name="Масляный фильтр", oem_number="11427953129", brand="Knecht", part_number="OX387D", price=460.0)]
        ), current_client=client, db=db)
        print(f"   Успех! Заказ #{order.id} оформлен на сумму {order.total_price} грн")

        print("5. Админ берет заказ в сборку, загружает фото и вносит ТТН Новой Почты...")
        updated_order = update_order_status(
            order_id=order.id,
            data=OrderStatusUpdate(
                status="shipped",
                assembly_photo_url="https://imgur.com/photo_assembled.jpg",
                ttn_number="20450897123456",
                purchase_cost=310.0
            ),
            db=db
        )
        print(f"   Успех! Статус: {updated_order.status}")
        print(f"   ТТН НП: {updated_order.ttn_number}")
        print(f"   Ссылка трекинга Новой Почты: {updated_order.ttn_tracking_url}")

        print("6. Проверка отображения заказа у клиента...")
        my_orders = get_my_orders(current_client=client, db=db)
        assert len(my_orders) == 1, "Ошибка: Заказ не найден у клиента!"
        assert my_orders[0].ttn_tracking_url == "https://novaposhta.ua/tracking/?cargo_number=20450897123456"
        print("   Клиент видит ТТН Новой Почты и ссылку трекинга!")

        print("7. Повтор заказа из истории...")
        rep_res = repeat_order(order_id=order.id, current_client=client, db=db)
        print(f"   Успех повтора! Новый запрос #{rep_res['new_request_id']} отправлен эксперту!")

        print("\nALL PHASE 4 TESTS PASSED SUCCESSFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase4_complete()
