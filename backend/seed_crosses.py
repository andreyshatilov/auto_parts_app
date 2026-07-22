"""
Скрипт автономного наповнення бази знань крос-номерів (seed_crosses.py).

Сканує файли Word (.docx) у папці scratch/Приложение за допомогою python-docx та regex,
витягує паралелі "OE Номер -> Бренд Аналога -> Артикул -> Ціна"
та зберігає їх у таблицю `cross_references` БЕЗ використання ШІ.
"""

import os
import re
from docx import Document
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import CrossReference

# Папка з файлами подборів .docx
DOCS_DIR = r"C:\Users\andre\.gemini\antigravity\scratch\Приложение"

def clean_oem(oem_str: str) -> str:
    """Видаляє всі пробіли, дефіси та крапки для точного пошуку в БД"""
    return re.sub(r"[^a-zA-Z0-9]", "", oem_str).upper()

def seed_cross_references():
    print("1. Створення таблиць БД (якщо відсутні)...")
    Base.metadata.create_all(bind=engine)
    
    db: SessionLocal = SessionLocal()
    records_added = 0

    try:
        if not os.path.exists(DOCS_DIR):
            print(f"⚠️ Папка {DOCS_DIR} не знайдена!")
            return

        docx_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".docx") and not f.startswith("~$")]
        print(f"2. Знайдено Word-файлів підборів: {len(docx_files)}")

        for file_name in docx_files:
            file_path = os.path.join(DOCS_DIR, file_name)
            try:
                doc = Document(file_path)
                lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

                current_category = "Запчастина"
                current_oe = None

                for i, line in enumerate(lines):
                    # 1. Шукаємо оригінальний номер
                    if "Оригінальний номер" in line or "Оригинальный номер" in line:
                        current_oe = re.sub(r"Ориг[іи]нальн[иы]й номер", "", line, flags=re.IGNORECASE).strip()
                        if i > 0 and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", lines[i - 1]):
                            current_category = lines[i - 1]
                        continue

                    # 2. Шукаємо аналоги (за наявністю тире '–' або '-' та 'грн')
                    if current_oe and ("–" in line or "-" in line) and "грн" in line:
                        # Приклад: Purflux L376 – 330 грн
                        clean_oem_val = clean_oem(current_oe)
                        if not clean_oem_val:
                            continue

                        # Розбиваємо за тире
                        parts = re.split(r"[–-]", line)
                        brand_and_code = parts[0].strip()
                        price_part = parts[1].strip() if len(parts) > 1 else ""

                        # Парсимо ціну
                        price_match = re.search(r"(\d+[\d\s]*)\s*грн", price_part)
                        if not price_match:
                            continue
                        price_val = float(price_match.group(1).replace(" ", ""))

                        # Розбиваємо бренд та артикул за першим пробілом
                        bc_parts = brand_and_code.split(maxsplit=1)
                        brand = bc_parts[0].strip()
                        part_number = bc_parts[1].strip() if len(bc_parts) > 1 else ""

                        if brand and part_number:
                            # Перевіряємо, чи немає вже такого кроса
                            existing = db.query(CrossReference).filter(
                                CrossReference.oem_number_clean == clean_oem_val,
                                CrossReference.brand == brand,
                                CrossReference.part_number == part_number
                            ).first()

                            if existing:
                                existing.times_used += 1
                                existing.price = price_val
                            else:
                                cross = CrossReference(
                                    oem_number_clean=clean_oem_val,
                                    oem_number_raw=current_oe,
                                    category_name=current_category,
                                    brand=brand,
                                    part_number=part_number,
                                    price=price_val,
                                    source_file=file_name
                                )
                                db.add(cross)
                                records_added += 1

            except Exception as e:
                print(f"   Помилка читання файлу {file_name}: {e}")

        db.commit()
        print(f"\nUSPESHNO! Dodano {records_added} novekh cross-nomeriv u bazu znan!")


    finally:
        db.close()

if __name__ == "__main__":
    seed_cross_references()
