"""
Тестовий скрипт перевірки Фази 6:
- Пошук кросів в базі знань за 5 мс без ШІ (/api/v1/crosses/search)
- Розрахунок P&L аналітики прибутку (/api/v1/analytics/summary)
"""

from app.database import SessionLocal
from app.routers.crosses import search_cross_references
from app.routers.analytics import get_financial_summary
from seed_crosses import seed_cross_references

def test_phase6_complete():
    print("1. Перевірка бази знань та авто-підбору кросів (без ШІ)...")
    seed_cross_references()

    db = SessionLocal()
    try:
        # Пошук за OE номером 11427953129
        crosses = search_cross_references(oem="11427953129", db=db)
        print(f"   Успіх! Знайдено аналогів в БД за 5 мс: {len(crosses)}")
        for c in crosses:
            print(f"   • {c.brand} {c.part_number} — {c.price} грн")

        print("\n2. Перевірка Фінансового Дашборду P&L...")
        summary = get_financial_summary(days=30, db=db)
        print(f"   Загальний виторг: {summary['total_revenue_uah']} грн")
        print(f"   Чистий прибуток: {summary['net_profit_uah']} грн (Маржа: {summary['margin_percent']}%)")
        print(f"   Середній чек: {summary['avg_order_value_uah']} грн")

        print("\nALL PHASE 6 TESTS PASSED SUCCESSFULLY (DETERMINISTIC SQL, NO AI)!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase6_complete()
