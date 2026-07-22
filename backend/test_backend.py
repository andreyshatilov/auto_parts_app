"""
Тестовый скрипт проверки бэкенд API и Базы Данных.
"""

from app.database import engine, Base, SessionLocal
from app.models import Car
from app.schemas import CarCreate
from app.routers.cars import create_car, get_cars

def test_all():
    print("1. DB tables init...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("2. Test car addition...")
        test_car_data = CarCreate(
            vin="WBAFP31010C502209",
            brand="BMW",
            model="523i",
            modification="F10",
            release_date="14.05.2010",
            engine_code="N52N",
            drive_type="RWD (Задний)",
            transmission_type="АКПП (Автомат)",
            transmission_code="8HP",
            notes="Test car BMW"
        )
        
        # Cleanup
        existing = db.query(Car).filter(Car.vin == test_car_data.vin).first()
        if existing:
            db.delete(existing)
            db.commit()
            
        new_car = create_car(test_car_data, db)
        print(f"   Success: Created car ID={new_car.id}, VIN={new_car.vin}, {new_car.brand} {new_car.model}")
        
        print("3. Test search car...")
        cars = get_cars(search="523i", skip=0, limit=10, db=db)
        print(f"   Found cars: {len(cars)}")
        assert len(cars) > 0, "Error: Car not found!"
        
        print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    test_all()
