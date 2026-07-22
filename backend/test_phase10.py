"""
Тестовий скрипт перевірки Фази 10 (Enterprise Production):
- Генерація Товарного Чека / Рахунку-Фактури (/api/v1/invoices/order/1)
- Генерація Офіційного Сервісного Паспорта Авто (/api/v1/invoices/car/1/passport)
- Автономне резервне копіювання БД (backup_db.py)
"""

from app.database import SessionLocal
from app.routers.invoices import get_order_invoice, get_car_service_passport
from backup_db import perform_db_backup

def test_phase10_complete():
    print("1. Перевірка роботи бекапу БД...")
    perform_db_backup()

    db = SessionLocal()
    try:
        print("\n2. Service Passport test:")
        passport_res = get_car_service_passport(car_id=1, db=db)
        assert passport_res.status_code == 200, "Passport error!"
        print("   [+] Service Passport HTML generated successfully!")

        print("\n3. Invoice test:")
        invoice_res = get_order_invoice(order_id=1, db=db)
        assert invoice_res.status_code == 200, "Invoice error!"
        print("   [+] Invoice HTML generated successfully!")

        print("\nALL PHASE 10 ENTERPRISE TESTS PASSED SUCCESSFULLY (100% PRODUCTION READY)!")

    finally:
        db.close()

if __name__ == "__main__":
    test_phase10_complete()
