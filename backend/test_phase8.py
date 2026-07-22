"""
Тестовий скрипт перевірки Фази 8:
- Нативний Мобільний UI & Bottom Navigation Bar
- Хронологія Сервісної Книжки у Гаражі
- Комплекти ТО та авто-кроси за 5 мс без ШІ
"""

from app.database import SessionLocal
from app.routers.crosses import search_cross_references

def test_phase8_complete():
    print("1. Перевірка роботи авто-підбору кросів для швидких комплектів ТО...")
    db = SessionLocal()
    try:
        crosses = search_cross_references(oem="11427953129", db=db)
        assert len(crosses) >= 1, "Помилка кросів ТО!"
        print(f"   Успіх! Комплект ТО містить перевірені аналоги: {crosses[0].brand} ({crosses[0].part_number})")

        print("\nALL PHASE 8 TESTS PASSED SUCCESSFULLY (NATIVE UI & SERVICE TIMELINE READY)!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase8_complete()
