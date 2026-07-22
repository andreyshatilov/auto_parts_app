"""
Тестовый скрипт проверки регистрации, авторизации и личного гаража.
"""

from app.database import engine, Base, SessionLocal
from app.models import Client, Car
from app.schemas import ClientRegister, ClientLogin, CarCreate
from app.routers.auth import register_client, login_client, get_current_client
from app.routers.clients import add_car_to_my_garage, get_all_clients

def test_phase2_flow():
    print("1. Re-creating DB tables for schema update...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("2. Testing client registration...")
        test_phone = "+380931234567"
        reg_data = ClientRegister(
            first_name="Ivan",
            last_name="Petrov",
            middle_name="Igorevich",
            phone=test_phone,
            shipping_address="Dnipro, NP #12",
            has_messenger=True
        )

        res = register_client(reg_data, db)
        token = res["auth_token"]
        client = res["client"]
        print(f"   Success! Created client ID={client.id}, Name={client.first_name}, Token={token[:15]}...")

        print("3. Testing session token validation...")
        fetched_client = get_current_client(x_auth_token=token, authorization=None, db=db)
        assert fetched_client.id == client.id, "Error: Token mismatch!"
        print("   Token validated successfully!")

        print("4. Testing adding car to client garage...")
        car_data = CarCreate(
            vin="WAUZZZ4B11N012345",
            brand="Audi",
            model="A6",
            modification="C5 2.4 tfsi",
            engine_code="BDV",
            transmission_type="MKPP",
            status="Identified"
        )
        new_car = add_car_to_my_garage(car_data, current_client=fetched_client, db=db)
        print(f"   Success! Added car to garage: {new_car.brand} {new_car.model} (VIN: {new_car.vin}, Owner ID: {new_car.client_id})")

        print("5. Testing client login by phone...")
        login_res = login_client(ClientLogin(phone=test_phone), db)
        assert login_res["auth_token"] == token, "Error: Token changed after login!"
        assert len(login_res["client"].cars) == 1, "Error: Car not found in garage!"
        print(f"   Success login! Found car in garage: {login_res['client'].cars[0].brand} {login_res['client'].cars[0].model}")

        print("6. Testing admin clients list visibility...")
        all_clients = get_all_clients(search="Petrov", skip=0, limit=10, db=db)
        print(f"   Admin sees clients count: {len(all_clients)}")
        assert len(all_clients) > 0, "Error: Admin cannot see client!"

        print("\nALL PHASE 2 TESTS PASSED SUCCESSFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase2_flow()
