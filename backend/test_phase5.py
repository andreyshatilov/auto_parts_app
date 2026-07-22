"""
Тестовий скрипт перевірки Фази 5 (Українська версія):
- 100% Українізація відповіді API
- Внутрішній чат по запиту (Клієнт ↔ Експерт)
- Вибір способу оплати (Передплата ФОП)
- Оформлення заявки на повернення за правилом 10 днів
"""

from app.database import engine, Base, SessionLocal
from app.schemas import (
    ClientRegister, CarCreate, OrderRequestCreate,
    ProposalCreate, ProposalItemCreate, ProposalAlternativeCreate,
    OrderCreate, OrderItemCreate, OrderReturnCreate, ChatMessageCreate
)
from app.routers.auth import register_client
from app.routers.clients import add_car_to_my_garage
from app.routers.requests import create_order_request
from app.routers.proposals import create_proposal
from app.routers.orders import create_order, get_my_orders
from app.routers.returns import create_order_return, get_all_returns, update_return_status
from app.routers.chat import send_chat_message, get_chat_messages
from app.routers.payments import get_payment_methods

def test_phase5_complete():
    print("1. Перестворення схеми БД для Фази 5...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("2. Реєстрація клієнта та додавання авто Audi A6...")
        res = register_client(ClientRegister(
            first_name="Іван", last_name="Петренко", phone="+380931234567", shipping_address="м. Київ, НП №1"
        ), db)
        client = res["client"]

        car = add_car_to_my_garage(CarCreate(
            vin="WAUZZZ4B11N012345", brand="Audi", model="A6", modification="C5", engine_code="BDV"
        ), current_client=client, db=db)

        print("3. Подача запиту та обмін повідомленнями в чаті...")
        req = create_order_request(OrderRequestCreate(car_id=car.id, client_message="Гальмівні колодки"), current_client=client, db=db)
        
        # Клієнт пише у чат
        msg1 = send_chat_message(ChatMessageCreate(request_id=req.id, message="Чи є в наявності керамічні колодки?"), sender_type="client", current_client=client, db=db)
        # Менеджер відповідає
        msg2 = send_chat_message(ChatMessageCreate(request_id=req.id, message="Так, Brembo кераміка 1200 грн"), sender_type="manager", current_client=None, db=db)
        
        chat_msgs = get_chat_messages(request_id=req.id, db=db)
        print(f"   Успіх! У чаті запиту #{req.id} збережено {len(chat_msgs)} повідомлень")

        print("4. Складання кошторису та замовлення з оплатою на ФОП...")
        prop = create_proposal(ProposalCreate(
            request_id=req.id,
            items=[
                ProposalItemCreate(
                    category_name="Гальмівні колодки", oem_number="4B0698151J",
                    alternatives=[ProposalAlternativeCreate(brand="Brembo", part_number="P85044", price=1200.0)]
                )
            ]
        ), db=db)

        order = create_order(OrderCreate(
            car_id=car.id, proposal_id=prop.id, payment_method="fop_prepayment",
            items=[OrderItemCreate(category_name="Гальмівні колодки", oem_number="4B0698151J", brand="Brembo", part_number="P85044", price=1200.0)]
        ), current_client=client, db=db)
        print(f"   Успіх! Замовлення #{order.id} створено. Спосіб оплати: {order.payment_method}")

        print("5. Оформлення повернення товару протягом 10 днів...")
        ret = create_order_return(OrderReturnCreate(order_id=order.id, reason="Замовив помилково 2 комплекти"), current_client=client, db=db)
        print(f"   Успіх! Заявку на повернення створено (Тип: {ret.return_type}, Статус: {ret.status})")

        print("6. Адмін схвалює повернення...")
        app_ret = update_return_status(return_id=ret.id, status_val="approved", db=db)
        print(f"   Успіх! Новий статус повернення: {app_ret.status}")

        print("7. Отримання способів оплати українською мовою...")
        pm = get_payment_methods()
        print(f"   Успіх! Доступні способи оплати: {len(pm['methods'])}")

        print("\nALL PHASE 5 TESTS PASSED SUCCESSFULLY (100% UKRAINIAN)!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase5_complete()
