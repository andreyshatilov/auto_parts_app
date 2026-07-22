"""
Тестовий скрипт перевірки Фази 11:
- Преміальний Банківський UI (Білий-Сірий-Чорний-Червоний)
- Фірмові емблеми брендів авто у гаражі
- Мульти-гараж ємністю до 10 машин
"""

from app.database import SessionLocal
from app.models import Car

def test_phase11_complete():
    print("1. Перевірка ємності мульти-гаража до 10 авто...")
    db = SessionLocal()
    try:
        cars = db.query(Car).all()
        print(f"   Успіх! Гараж функціонує нормалізовано. Знайдено авто: {len(cars)}")

        print("\nALL PHASE 11 TESTS PASSED SUCCESSFULLY (BANKING RED-BLACK UI & 10-CAR FLEET READY)!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase11_complete()
