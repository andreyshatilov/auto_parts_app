"""
Тестовий скрипт перевірки Фази 7:
- Довідник міст та відділень Нової Пошти (/api/v1/novaposhta/cities, /api/v1/novaposhta/branches)
- Експорт реєстрів у файлах CSV (/api/v1/exports/clients/csv, /api/v1/exports/orders/csv)
"""

from app.database import SessionLocal
from app.routers.novaposhta import get_cities, get_branches
from app.routers.exports import export_clients_csv, export_orders_csv

def test_phase7_complete():
    print("1. Перевірка довідника Нової Пошти...")
    cities = get_cities(query="Дніпро")
    assert len(cities) >= 1, "Помилка міст НП!"
    print(f"   Успіх! Знайдено місто: {cities[0]['name']}")

    branches = get_branches(city_id="dnipro")
    assert len(branches["branches"]) >= 1, "Помилка відділень НП!"
    print(f"   Успіх! Знайдено {len(branches['branches'])} відділень НП у Дніпрі!")

    db = SessionLocal()
    try:
        print("\n2. Перевірка генерації CSV-звітів...")
        res_clients = export_clients_csv(db=db)
        assert res_clients.status_code == 200, "Помилка експорту клієнтів!"
        print("   Успіх! CSV реєстр клієнтів згенеровано!")

        res_orders = export_orders_csv(db=db)
        assert res_orders.status_code == 200, "Помилка експорту замовлень!"
        print("   Успіх! CSV реєстр замовлень згенеровано!")

        print("\nALL PHASE 7 TESTS PASSED SUCCESSFULLY (PRODUCTION READY)!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase7_complete()
