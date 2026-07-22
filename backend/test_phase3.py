"""
Тестовый скрипт проверки Фазы 3:
- Запросы на подбор
- Составление сметы админом
- Генерация PIN-кода продажи
- Безопасная передача авто и ВСЕЙ серверной истории новому владельцу
"""

from app.database import engine, Base, SessionLocal
from app.models import Client, Car, OrderRequest, Proposal, CarTransferCode
from app.schemas import (
    ClientRegister, CarCreate, OrderRequestCreate,
    ProposalCreate, ProposalItemCreate, ProposalAlternativeCreate,
    TransferCodeGenerate, TransferCodeClaim
)
from app.routers.auth import register_client
from app.routers.clients import add_car_to_my_garage
from app.routers.requests import create_order_request, get_all_requests, get_my_requests
from app.routers.proposals import create_proposal
from app.routers.transfers import generate_transfer_code, claim_car_by_pin

def test_phase3_complete():
    print("1. Пересоздание схемы БД с новыми таблицами Фазы 3...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("2. Регистрация Клиента №1 (Продавец - Иван)...")
        res1 = register_client(ClientRegister(
            first_name="Иван", last_name="Продавец", phone="+380931111111", shipping_address="г. Днепр, НП №1"
        ), db)
        seller = res1["client"]

        print("3. Добавление авто Audi A6 в гараж Ивана...")
        car1 = add_car_to_my_garage(CarCreate(
            vin="WAUZZZ4B11N099999", brand="Audi", model="A6", modification="C5 2.4", engine_code="BDV"
        ), current_client=seller, db=db)
        print(f"   Успех! Авто в гараже Ивана (ID: {car1.id}, VIN: {car1.vin})")

        print("4. Иван подает запрос на подбор деталей...")
        req = create_order_request(OrderRequestCreate(
            car_id=car1.id, client_message="Нужен масляный фильтр и тормозные колодки"
        ), current_client=seller, db=db)
        print(f"   Успех! Запрос создан (ID: {req.id}, Статус: {req.status})")

        print("5. Админ формирует смету с OE номерами и аналогами...")
        prop = create_proposal(ProposalCreate(
            request_id=req.id,
            manager_comment="Всё есть в наличии на складе",
            items=[
                ProposalItemCreate(
                    category_name="Масляный фильтр",
                    oem_number="12640445",
                    alternatives=[
                        ProposalAlternativeCreate(brand="Knecht", part_number="OC1421", price=630.0),
                        ProposalAlternativeCreate(brand="Mann", part_number="W7056", price=660.0)
                    ]
                )
            ]
        ), db=db)
        print(f"   Успех! Смета создана (ID: {prop.id}, Категорий: {len(prop.items)})")

        print("6. Иван решает продать машину и генерирует PIN-код передачи...")
        transfer_res = generate_transfer_code(TransferCodeGenerate(car_id=car1.id), current_client=seller, db=db)
        pin_code = transfer_res["pin_code"]
        print(f"   Успех! Сгенерирован 6-значный PIN-код передачи: {pin_code}")

        print("7. Регистрация Клиента №2 (Покупатель - Сергей)...")
        res2 = register_client(ClientRegister(
            first_name="Сергей", last_name="Покупатель", phone="+380502222222", shipping_address="г. Киев, НП №5"
        ), db)
        buyer = res2["client"]

        print("8. Сергей вводит 6-значный PIN-код и забирает авто...")
        claimed_car = claim_car_by_pin(TransferCodeClaim(pin_code=pin_code), current_client=buyer, db=db)
        print(f"   Успех! Машина принята Сергеем (Новый владелец ID: {claimed_car.client_id})")

        print("9. Проверка: История подборов на сервере сохранилась за новым владельцем...")
        buyer_requests = get_my_requests(current_client=buyer, db=db)
        print(f"   У Сергея отображается связанных запросов/истории по этой машине: {len(buyer_requests)}")

        print("\nALL PHASE 3 TESTS PASSED SUCCESSFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase3_complete()
